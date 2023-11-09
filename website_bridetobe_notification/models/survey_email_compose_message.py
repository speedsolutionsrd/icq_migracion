from odoo import models, fields, api, _, tools
import urlparse


# class SurveyMailComposeMessage(models.TransientModel):
#     _inherit = 'survey.mail.compose.message'
#
#     @api.multi
#     def send_mail(self, auto_commit=False):
#         survey_mail_compose_message = super(SurveyMailComposeMessage, self).send_mail()
#         SurveyUserInput = self.env['survey.user_input']
#         for wizard in self:
#             for partner_id in wizard.partner_ids:
#                 survey_user_input = SurveyUserInput.search([('survey_id', '=', wizard.survey_id.id),
#                                                             ('state', 'in', ['new', 'skip']), '|',
#                                                             ('partner_id', '=', partner_id.id),
#                                                             ('email', '=', partner_id.email)], limit=1)
#                 path = urlparse.urlparse(wizard.survey_id.public_url).path[1:]
#                 token = survey_user_input.token
#                 self.env['whatsapp.send.message'].action_send(payload={"phone": partner_id.mobile,
#                                                                        "body": tools.html2plaintext(
#                                                                            wizard.body).replace("__URL__",
#                                                                                                 path + '/' + token).replace('*', ''),
#                                                                        "partner_id": partner_id.id})
#         return survey_mail_compose_message
