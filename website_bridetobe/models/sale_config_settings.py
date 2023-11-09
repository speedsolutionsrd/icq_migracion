from odoo import models, fields, api

class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    #related='company_id.security_rental',store=True
    security_rental = fields.Integer("Rental Security Hours",config_parameter='sale_rental.rental_security_hours')

    # @api.multi
    # def set_deposit_product_id_defaults(self):
    #     return self.env['ir.values'].sudo().set_default(
    #         'sale.config.settings', 'deposit_product_id_setting', self.deposit_product_id_setting.id)