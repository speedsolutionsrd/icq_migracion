from odoo import models, fields, api


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    url_api = fields.Char(string="Api Url")
    auth_token = fields.Char(string="Token")
    whatsapp_number_id = fields.Char(string="Number ID")



    @api.model
    def get_default_url_api(self, field):
        return {
            'url_api': self.env['ir.values'].get_default('res.config.settings', 'url_api'),
        }

    @api.model
    def get_default_auth_token(self, field):
        return {
            'auth_token': self.env['ir.values'].get_default('res.config.settings', 'auth_token'),
        }

    @api.model
    def set_default(self):
        IrValues = self.env['ir.values']
        if self.env['res.users'].has_group('base.group_erp_manager'):
            IrValues = IrValues.sudo()
        IrValues.set_default('res.config.settings', 'url_api', self.url_api)
        IrValues.set_default('res.config.settings', 'auth_token', self.auth_token)