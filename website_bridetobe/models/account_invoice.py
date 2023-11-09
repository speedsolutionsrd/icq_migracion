from odoo import models, fields, api, tools
import json
from datetime import timedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    event_date = fields.Date(string="Fecha Evento")
    seller_id = fields.Many2one('hr.employee', string="Vendedor")
    delivery_state = fields.Boolean(string="Delivered", default=False)
    reception_state = fields.Boolean(string="Received", default=False)

    def _payment_is_inside(self, dict, journal_name, amount):
        for obj in dict:
            if obj['journal_name'] == journal_name:
                obj['amount'] += amount
                return True
        return False

    @api.model
    def get_payments(self):
        payment_ids = []
        if self.payments_widget:
            for obj in json.loads(self.payments_widget)['content']:
                if not self._payment_is_inside(payment_ids, obj.get('journal_name'), obj.get('amount')):
                    payment_ids.append({'journal_name': obj.get('journal_name'),
                                        'amount': obj.get('amount')})
            return payment_ids
        else:
            return False

    def process_delivery(self):
        related_picking = self.env['stock.picking'].sudo().search(
            [('origin', '=', self.origin), ('picking_type_code', '=', 'outgoing')])
        related_picking.force_assign()
        self.delivery_state = True
        return related_picking.process_transfer()

    def process_reception(self):
        related_picking = self.env['stock.picking'].sudo().search(
            [('origin', '=', self.origin), ('picking_type_code', '=', 'incoming')])
        related_picking.force_assign()
        self.reception_state = True
        return related_picking.process_transfer()

    def print_reception_receipt(self):
        return self.env['posbox.print'].posbox_send_ticket('website_bridetobe.report_ticket_recepcion_invoice',
                                                                  {'invoice': self, 'company': self.company_id})

    def print_receipt(self):
        return self.env['posbox.print'].posbox_send_ticket('website_bridetobe.report_account_invoice_ticket',
                                                           {'invoice': self, 'company': self.company_id})

    def receipt_no_test_message(self):
        message_body = self.env['sale.rental.custom.message'].get_message(self, 'delivery_state',
                                                                          False).message_body.format(
            self.partner_id.name,
            ",".join(self.invoice_line_ids.mapped('product_id').mapped('barcode')),
            ".",
            ".",
            ".",
            ".",
            ".",
            ".",
            str(fields.Datetime.from_string(fields.Datetime.now()) + timedelta(hours=-4)),
            ".",
            ".")
        return message_body

    def print_receipt_no_test(self):
        message_body = self.receipt_no_test_message()
        return self.env['posbox.print'].posbox_send_ticket('website_bridetobe.report_account_invoice_ticket_no_test',
                                                           {'invoice': self, 'company': self.company_id,
                                                            'message_body': tools.html2plaintext(message_body)})
