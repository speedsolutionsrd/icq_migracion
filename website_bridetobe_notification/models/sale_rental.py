# -*- coding: utf-8 -*-
from odoo import models, tools, api, _, fields
from datetime import timedelta


class SaleRental(models.Model):
    _inherit = 'sale.rental'

    def post_message(self, message_body, custom_message, parameters):
        message_body = super(SaleRental, self).post_message(message_body)
        # if message_body:
        #     self.env['whatsapp.send.message'].action_send(payload={"phone": self.partner_id.mobile,
        #                                                            "body": tools.html2plaintext(message_body).replace(
        #                                                                '*', ''),
        #                                                            "partner_id": self.partner_id.id})
        if custom_message.whatsapp_template_id:
            body_components = []
            for parameter in custom_message.whatsapp_template_body_parameter_ids.sorted(key=lambda x:int(x.value)):
                body_components.append(parameters[int(parameter.value)])
            custom_message.whatsapp_template_id.sudo().send_template(self.partner_id.mobile, body_components=body_components)
        return message_body

    def send_return_email(self):
        custom_message, parameters = super(SaleRental, self).send_return_email()[0]
        # print(type(message_body))
        # print(parameters)
        # for message in message_body:
        #     self.env['whatsapp.send.message'].action_send(payload={"phone": self.partner_id.mobile,
        #                                                            "body": tools.html2plaintext(message),
        #                                                            "partner_id": self.partner_id.id})
        if custom_message.whatsapp_template_id:
            body_components = []
            for parameter in custom_message.whatsapp_template_body_parameter_ids.sorted(key=lambda x:int(x.value)):
                body_components.append(parameters[int(parameter.value)])
            custom_message.whatsapp_template_id.send_template(self.partner_id.mobile, body_components=body_components)
        return custom_message.message_body.format(*parameters)

    def process_reception(self):
        custom_message = self.env['sale.rental.custom.message'].get_message(self.env['account.invoice'],
                                                                            'reception_state', False)
        parameters = [self.partner_id.name,
                      self.rental_product_id.barcode or ".",
                      self.state_internal.name,
                      self.modista.name,
                      self.start_order_id.name,
                      self.test_date,
                      self.delivery_date,
                      self.current_days,
                      self.start_date,
                      self.old_rental_product_id.barcode,
                      "."]
        # self.env['whatsapp.send.message'].action_send(payload={"phone": self.partner_id.mobile,
        #                                                        "body": tools.html2plaintext(message_body),
        #                                                        "partner_id": self.partner_id.id})
        if custom_message.whatsapp_template_id:
            body_components = []
            for parameter in custom_message.whatsapp_template_body_parameter_ids.sorted(key=lambda x:int(x.value)):
                body_components.append(parameters[int(parameter.value)])
            custom_message.whatsapp_template_id.send_template(self.partner_id.mobile, body_components=body_components)
        return super(SaleRental, self).process_reception()
