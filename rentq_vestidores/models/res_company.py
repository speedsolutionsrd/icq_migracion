from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    vestidor_printer_url = fields.Char(string='Printer Url')