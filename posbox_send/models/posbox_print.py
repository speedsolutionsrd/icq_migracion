from odoo import models, fields, api
import urllib.request, json
from odoo.exceptions import ValidationError


class PosboxPrint(models.TransientModel):
    _name = "posbox.print"
    _inherit = 'res.config.settings'
    _description = "Print directly to Posbox"

    default_posbox_name = fields.Char(string="Description",
                                      default="Posbox Send Settings",
                                      default_model="posbox.print")

    default_posbox_url = fields.Char(string="PosBox URL", default_model="posbox.print")
    default_posbox_state = fields.Selection([('complete', 'Validate'),
                                             ('fail', 'Fail')], string="State", default_model="posbox.print")
    default_posbox_printer_state = fields.Char(string="Printer Status", default_model="posbox.print")
    default_posbox_printer_info = fields.Char(string="Printer Info", default_model="posbox.print")

    receipt = fields.Text(string="Receipt")
    receipt_url = fields.Text(string="default_posbox_url")

    def check_posbox_connection(self):
        receipt_url = self.default_posbox_url
        receipt_render = self.env['report'].render('posbox_send.PosboxPrintTest', {'posbox_url': receipt_url})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Print Receipt',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'posbox.print',
            'context': {"default_receipt_url": receipt_url,
                        "default_receipt": receipt_render
                        },
            'view_id': self.env.ref('posbox_send.posbox_print_receipt_form').id,
            'target': 'new',
        }

    @api.model
    def posbox_send_ticket(self, report_name, report_data, posbox_url=False):
        if posbox_url:
            receipt_url = posbox_url
        else:
            receipt_url = self.search([], limit=1, order='id desc').default_posbox_url
        receipt_render = self.env['report'].render(report_name, report_data)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Print Receipt',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'posbox.print',
            'context': {"default_receipt_url": receipt_url,
                        "default_receipt": receipt_render},
            'view_id': self.env.ref('posbox_send.posbox_print_receipt_form').id,
            'target': 'new'
        }