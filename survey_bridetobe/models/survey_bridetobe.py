from odoo import models, fields, api


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    survey_id = fields.Many2one('survey.survey', string="Survey")

    @api.model
    def set_survey_id_defaults(self):
        return self.env['ir.values'].sudo().set_default('sale.config.settings', 'survey_id', self.survey_id.id)
