from odoo import models, fields, api


class StockSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    label_printer_url = fields.Char(string="Label Print URL", default='ZD410',config_parameter='stock.config.settings')

    # @api.model
    # def set_label_printer_url(self):
    #     return self.env['ir.values'].sudo().set_default('stock.config.settings', 'label_printer_url',
    #                                                     self.label_printer_url)
