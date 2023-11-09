from odoo import models, fields, api


class SendSurveyBridetobe(models.TransientModel):
    _name = 'send.survey.bridetobe'
    _description = 'Send Survey'

    survey_id = fields.Many2one('survey.survey', string="Encuesta")
    partner_id = fields.Many2one('res.partner', string="Cliente")
    email = fields.Char(related='partner_id.email', string="Email")
    rental_id = fields.Many2one('sale.rental')

    def send_survey(self):
        self.rental_id.send_survey(self.survey_id)
