from odoo import models, fields, api
from datetime import timedelta


class Pickup(models.Model):
    _inherit = 'pickup.pickup'
    _rec_name = "rental_id"

    rental_id = fields.Many2one('sale.rental', string="Renta", required=True)
    event_date = fields.Date('Fecha Evento', related="rental_id.end_date")
    payment_status = fields.Selection(related="rental_id.payment_status", string="Saldo")
    partner_id = fields.Many2one(related="rental_id.partner_id", string='Cliente')
    estimated_date = fields.Date('tiempo estimado', compute='_compute_estimated_date', readonly=True)

    @api.depends('rental_id')
    def _compute_estimated_date(self):
        for pickup in self:
            if pickup.rental_id:
                pickup.estimated_date = (
                            fields.Datetime.from_string(pickup.rental_id.end_date) + timedelta(days=2)).date()

    def post_message(self, message_body, custom_message, parameters):
        # message_body = super(Pickup, self).post_message(message_body)
        if custom_message.whatsapp_template_id:
            body_components = []
            for parameter in parameters:
                print(parameters)
                print(parameter)
                body_components.append(str(parameter))
            custom_message.whatsapp_template_id.sudo().send_template(self.partner_id.mobile,
                                                                     body_components=body_components)
        return message_body

    def write(self, vals):
        if vals.get('status') == 'pickup':
            custom_message = self.env['sale.rental.custom.message'].sudo().search(
                [('available_model_id.model_name', '=', 'pickup.pickup'),
                 ('ir_model_field_id.name', '=', 'status')])
            message_body = custom_message.message_body
            params = [str(self.partner_id.name), str(self.rental_id.rental_product_id.default_code),
                      str(fields.Date.today())]
            self.post_message(message_body, custom_message, params)
        return super(Pickup, self).write(vals)
