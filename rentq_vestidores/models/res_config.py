from odoo import models, fields


class VestidoresConfigSettings(models.TransientModel):
    _name = 'rentq.vestidores.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    vestidor_printer_url = fields.Char(related='company_id.vestidor_printer_url')