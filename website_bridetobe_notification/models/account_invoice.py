from datetime import datetime

import pytz
from datetime import timedelta
from odoo import models, tools, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def send_rental_message(self, product_ids, subject, message_body):
        if self.origin:
            order_id = self.env['sale.order'].search([('name', '=', self.origin)])

            rental_id = self.env['sale.rental'].search([('start_order_id', '=', order_id.id),
                                                        ('rental_product_id', 'in', product_ids.ids)])

            if rental_id:
                rental_id.message_ids.create({"subject": subject,
                                              "subtype_id": 1,
                                              "res_id": rental_id.id,
                                              "partner_ids": [(4, self.partner_id.id)],
                                              "needaction_partner_ids": [(4, self.partner_id.id)],
                                              "body": message_body,
                                              "record_name": rental_id.display_name,
                                              "date": fields.Datetime.now(),
                                              "model": 'sale.rental',
                                              "author_id": self.env.user.id,
                                              "message_type": "email",
                                              "email_from": self.env.user.email})

    def process_reception(self):
        for line_id in self.invoice_line_ids:
            custom_message = self.env['sale.rental.custom.message'].get_message(self, 'reception_state', False)
            body_parameters = [line_id.partner_id.name,
                               line_id.product_id.barcode or ".",
                               ".",
                               ".",
                               ".",
                               ".",
                               ".",
                               ".",
                               str(fields.Datetime.from_string(fields.Datetime.now()) + timedelta(hours=-4)),
                               ".",
                               "."]
            message_body = custom_message.message_body.format(*body_parameters)
            # self.env['whatsapp.send.message'].action_send(payload={"phone": self.partner_id.mobile,
            #                                                        "body": tools.html2plaintext(message_body),
            #                                                        "partner_id": self.partner_id.id})

            self.send_rental_message(line_id.product_id.product_tmpl_id, "Recepcion", message_body)

            if custom_message.whatsapp_template_id:
                body_components = []
            for parameter in custom_message.whatsapp_template_body_parameter_ids.sorted(key=lambda x: int(x.value)):
                body_components.append(body_parameters[int(parameter.value)])

            custom_message.whatsapp_template_id.send_template(line_id.partner_id.mobile,
                                                              body_components=body_components)
        return super(AccountInvoice, self).process_reception()

    def print_receipt_no_test(self):
        custom_message = self.env['sale.rental.custom.message'].get_message(self, 'delivery_state', False)
        body_parameters = [self.partner_id.name,
                           ",".join(self.invoice_line_ids.mapped('product_id').mapped('barcode')),
                           ".",
                           ".",
                           ".",
                           ".",
                           ".",
                           ".",
                           str(fields.Datetime.from_string(fields.Datetime.now()) + timedelta(hours=-4)),
                           ".",
                           "."]
        message_body = tools.html2plaintext(custom_message.message_body.format(*body_parameters))
        # self.env['whatsapp.send.message'].action_send(payload={"phone": self.partner_id.mobile,
        #                                                        "body": message_body,
        #                                                        "partner_id": self.partner_id.id})
        if custom_message.sudo().whatsapp_template_id:

            body_components = []
            for parameter in custom_message.whatsapp_template_body_parameter_ids.sorted(key=lambda x: int(x.value)):
                body_components.append(body_parameters[int(parameter.value)])

            custom_message.sudo().whatsapp_template_id.send_template(self.partner_id.mobile, body_components=body_components)

        self.send_rental_message(self.invoice_line_ids.mapped('product_id').mapped('product_tmpl_id'),
                                 "Entrega sin Prueba", message_body)

        return self.env['posbox.print'].posbox_send_ticket('website_bridetobe.report_account_invoice_ticket_no_test',
                                                           {'invoice': self, 'company': self.company_id,
                                                            'message_body': message_body})
