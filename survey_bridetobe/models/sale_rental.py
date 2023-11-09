from odoo import models, fields, _
from odoo.exceptions import UserError


class SaleRental(models.Model):
    _inherit = 'sale.rental'

    def survey_data(self, view_id):

        survey = self.env['survey.survey'].browse(
            self.env['ir.values'].get_default('sale.config.settings', 'survey_id'))

        template = survey.env.ref('survey.email_template_survey', raise_if_not_found=False)
        local_context = dict(
            survey.env.context,
            default_model='survey.survey',
            default_res_id=survey.id,
            default_survey_id=survey.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            default_public='email_private',
            default_partner_ids=[self.partner_id.id],
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'survey.mail.compose.message',
            'target': 'new',
            'view_id': view_id,
            'context': local_context,
        }

    def send_survey(self):
        if self.env['ir.values'].get_default('sale.config.settings', 'survey_id'):
            return self.survey_data([self.env.ref('survey_bridetobe.survey_email_compose_message').id])
        else:
            raise UserError("Encuesta no definida")

    def send_survey_wizard(self):
        return self.survey_data([self.env.ref('survey_bridetobe.survey_email_compose_message_details').id])
