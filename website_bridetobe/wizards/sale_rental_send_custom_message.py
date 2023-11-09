from odoo import models, fields, api
from datetime import timedelta, datetime


class SaleRentalSendCustomMessage(models.Model):
    _name = "sale.rental.send.custom.message"
    _inherit = 'mail.thread'

    message_template = fields.Many2one("sale.rental.custom.message", string="Message Template")
    message_body = fields.Html(string="Message Body")
    partner_id = fields.Many2one("res.partner", string="Partner")
    mobile = fields.Char(related="partner_id.mobile", string="Mobile")
    rental_id = fields.Many2one('sale.rental')

    def generate_message_body(self):
        if self.message_template.message_body:
            change_rental_product_date = ""
            if self.rental_id.change_rental_product_date:
                rental_product_date = fields.Datetime.from_string(
                    self.rental_id.change_rental_product_date) + timedelta(hours=-4)
                change_rental_product_date = datetime.strftime(rental_product_date, '%d/%m/%Y %I:%M %p')
            message_body = self.message_template.message_body.format(
                self.partner_id.name,
                self.rental_id.rental_product_id.barcode or ".",
                self.rental_id.state_internal.name,
                self.rental_id.modista.name,
                self.rental_id.start_order_id.name,
                self.rental_id.test_date,
                self.rental_id.delivery_date,
                self.rental_id.current_days,
                self.rental_id.start_date,
                self.rental_id.old_rental_product_id.barcode,
                change_rental_product_date,
            )
            return message_body
        else:
            return self.message_body

    @api.onchange('message_template')
    def change_message_template(self):
        self.message_body = self.generate_message_body()

    def action_send(self):
        message_body = self.generate_message_body()
        self.message_ids.create({
            "subject": "Detalles de su Renta" + self.rental_id.start_order_id.name,
            "subtype_id": 1,
            "res_id": self.rental_id.id,
            "partner_ids": [(4, self.partner_id.id)],
            "needaction_partner_ids": [(4, self.partner_id.id)],
            "body": message_body,
            "record_name": self.rental_id.display_name,
            "date": fields.Datetime.now(),
            "model": 'sale.rental',
            "author_id": self.env.user.id,
            "message_type": "email",
            "email_from": self.env.user.email})
        return message_body
