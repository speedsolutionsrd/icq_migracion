from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class LoyaltyPointPaidWizard(models.TransientModel):
    _name = 'loyalty.point.paid.wizard'
    _description = "Wizard to points Redeem"

    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    partner_id = fields.Many2one('res.partner', string="Customer", compute="change_loyalty_card_id")
    loyalty_card_id = fields.Many2one('loyalty.card', string="Card Used",
                                      domain="[('partner_id','!=',False)]")
    card_points = fields.Integer(string="Available Points", compute="change_loyalty_card_id")
    points_to_use = fields.Integer(string="Points to Use")

    def get_available_points(self, loyalty_card=False):
        point_total = 0
        invoice_points = 0
        loyalty_card_id = self.env['loyalty.card'].browse(loyalty_card or self._context.get("default_loyalty_card_id"))
        invoice_id = self.env['account.invoice'].browse(self._context.get("default_invoice_id"))
        for point in self.env['loyalty.card.point'].search([('name', '=', loyalty_card_id.id)]):
            if point.state == 'active':
                point_total += point.generated_points
            if point.invoice_id.id == invoice_id.id and point.generated_points > 0:
                invoice_points += abs(point.generated_points)
        return point_total - invoice_points

    @api.onchange("loyalty_card_id")
    def change_loyalty_card_id(self):
        self.partner_id = self.loyalty_card_id.partner_id
        self.card_points = self.get_available_points(self.loyalty_card_id.id)

    def redeem_points(self, data=False):
        paid_amount = 0.0
        equivalent_points = int(
            self.env['ir.values'].sudo().get_default('loyalty.config.settings', 'points_equivalent'))
        if equivalent_points == 0:
            raise ValidationError("Error con la equivalencia de Puntos Contacte su administrador")

        for paid in self.invoice_id.payment_ids:
            if paid.journal_id.code != 'RP':
                paid_amount += paid.amount

        points_value = self.points_to_use / equivalent_points

        if self.card_points < self.points_to_use:
            raise UserError("Selected points are les than available points")

        if paid_amount < self.invoice_id.amount_tax:
            raise UserError(
                "%s of Taxes must be paid in CASH before redeem points" % (self.invoice_id.amount_tax - paid_amount))

        if points_value > (self.invoice_id.amount_total - paid_amount):
            raise UserError(
                "You only need %s points to paid this invoice" % ((self.invoice_id.residual / equivalent_points)))

        payment_obj = self.env['account.payment']
        payment = payment_obj.create({'invoice_ids': [(4, self.invoice_id.id)],
                                      'journal_id': self.env['account.journal'].search(
                                          [('code', '=', ('RP'))], limit=1).id,
                                      'payment_method_id': self.env['account.payment.method'].search(
                                          [('code', '=', 'electronic')], limit=1).id,
                                      'amount': points_value,
                                      'payment_type': 'inbound',
                                      'partner_type': 'customer',
                                      'communication': 'Redencion Puntos de Lealtad Tarjeta %s' % self.loyalty_card_id.name,
                                      'partner_id': self.invoice_id.partner_id.id})
        payment.post()
        self.env['loyalty.card.point'].create({'name': self.loyalty_card_id.id,
                                               'generated_points': self.points_to_use * -1,
                                               'generation_date': datetime.today(),
                                               'invoice_id': self.invoice_id.id})
