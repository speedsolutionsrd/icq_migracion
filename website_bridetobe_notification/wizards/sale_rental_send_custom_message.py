from odoo import models, fields, api
from datetime import timedelta, datetime
from odoo.tools import html2plaintext


class SaleRentalSendCustomMessage(models.Model):
    _inherit = "sale.rental.send.custom.message"

    whatsapp_template_id = fields.Many2one(related="message_template.whatsapp_template_id")
    whatsapp_account_id = fields.Many2one("meta.connect.whatsapp.account", string="Whatsapp Account")

    def action_send(self):
        message_body = super(SaleRentalSendCustomMessage, self).action_send()

        parameters = [self.rental_id.partner_id.name,
                      self.rental_id.rental_product_id.barcode or ".",
                      self.rental_id.state_internal.name,
                      self.rental_id.modista.name,
                      self.rental_id.start_order_id.name,
                      self.rental_id.test_date,
                      self.rental_id.delivery_date,
                      self.rental_id.current_days,
                      self.rental_id.start_date,
                      self.rental_id.old_rental_product_id.barcode,
                      "."]
        if self.whatsapp_template_id:
            body_components = []
            for parameter in self.message_template.whatsapp_template_body_parameter_ids:
                body_components.append(parameters[int(parameter.value)])
            self.whatsapp_template_id.send_template(self.partner_id.mobile, body_components=body_components)
        elif self.whatsapp_account_id and not self.whatsapp_template_id:
            self.whatsapp_account_id.send_message(self.mobile, html2plaintext(message_body))

        return message_body
