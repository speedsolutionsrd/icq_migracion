from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = "account.move"

    loyalty_card = fields.Many2one('loyalty.card', string="Loyalty Card")

    @api.model
    def calc_loyalty_points(self):
        if self.loyalty_card:
            for invoice_line_id in self.invoice_line_ids:
                points_total = 0
                point_config = self.env['loyalty.card.cumulative.config'].search(
                    [('name', '=', invoice_line_id.product_id.categ_id.id)])

                if point_config:
                    if point_config.calc_type == 'value':
                        points_total = point_config.amount
                    elif point_config.calc_type == 'percent':
                        points_total = ((invoice_line_id.price_subtotal * invoice_line_id.quantity) * point_config.amount) / 100

                    time_valid = False
                    if point_config.loyalty_point_time > 0 and point_config.loyalty_point_time_period:
                        if point_config.loyalty_point_time_period == "days":
                            time_valid = datetime.today() + timedelta(days=point_config.loyalty_point_time)
                        elif point_config.loyalty_point_time_period == "months":
                            time_valid = datetime.today() + relativedelta(months=point_config.loyalty_point_time)

                    self.env['loyalty.card.point'].create({'name': self.loyalty_card.id,
                                                           'generated_points': points_total,
                                                           'generation_date': datetime.today(),
                                                           'expiration_date': time_valid,
                                                           'loyalty_config': point_config.id,
                                                           'product_id': invoice_line_id.product_id.id,
                                                           'invoice_id': self.id})
                    self.message_post(body="El articulo %s genero %s puntos" % (invoice_line_id.name, points_total))
                else:
                    self.message_post(body="El articulo %s no genero puntos" % invoice_line_id.name)

    # @api.multi
    # def action_invoice_open(self):
    #     if super(AccountMove, self).action_invoice_open():
    #         self.calc_loyalty_points()

    @api.model
    def action_post(self):
        if super(AccountMove, self).action_post():
            self.calc_loyalty_points()

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.loyalty_card = self.partner_id.loyalty_card_id
        return super(AccountMove, self)._onchange_partner_id()

    def loyalty_redempt(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Redempt Points',
            # 'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'loyalty.point.paid.wizard',
            'context': {"default_invoice_id": self.id,
                        "default_partner_id": self.partner_id.id,
                        "default_loyalty_card_id": self.partner_id.loyalty_card_id.id,
                        },
            'view_id': self.env.ref('loyalty_card.loyalty_point_paid_wizard').id,
            'target': 'new',
        }