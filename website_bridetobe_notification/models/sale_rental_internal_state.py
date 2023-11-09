from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleRentalInternalState(models.Model):
    _inherit = 'sale.rental.internal.state'

    whatsapp_template_id = fields.Many2one('meta.connect.whatsapp.template', string="Whatsapp Template")
    whatsapp_template_body = fields.Text(related="whatsapp_template_id.body")
    whatsapp_template_body_parameter_ids = fields.One2many('sale.rental.custom.message.parameter', 'state_id',
                                                           string="Parameters")
    parameter_count = fields.Integer(related='whatsapp_template_id.parameter_count')

    whatsapp_template_confeccion_id = fields.Many2one('meta.connect.whatsapp.template',
                                                      string="Whatsapp Template Confeccion")
    whatsapp_template_confeccion_body = fields.Text(related="whatsapp_template_confeccion_id.body")
    whatsapp_template_body_parameter_confeccion_ids = fields.One2many('sale.rental.custom.message.parameter.confeccion',
                                                                      'state_id',
                                                                      string="Parameters")
    parameter_count_confeccion = fields.Integer(related='whatsapp_template_confeccion_id.parameter_count')

    @api.constrains('whatsapp_template_body_parameter_confeccion_ids', 'whatsapp_template_confeccion_id')
    def _check_parameter_confeccion_ids(self):
        if self.parameter_count_confeccion == 0:
            self.whatsapp_template_body_parameter_confeccion_ids.unlink()
        if len(self.whatsapp_template_body_parameter_confeccion_ids) != self.parameter_count_confeccion:
            raise ValidationError(
                'Se requieren %s parametros para este template usted agrego %s' % (
                    self.whatsapp_template_confeccion_id.parameter_count,
                    len(self.whatsapp_template_body_parameter_ids)))

    @api.constrains('whatsapp_template_body_parameter_ids', 'whatsapp_template_id')
    def _check_parameter_ids(self):
        if self.parameter_count == 0:
            self.whatsapp_template_body_parameter_ids.unlink()
        if len(self.whatsapp_template_body_parameter_ids) != self.parameter_count:
            raise ValidationError(
                'Se requieren %s parametros para este template usted agrego %s' % (
                    self.whatsapp_template_id.parameter_count, len(self.whatsapp_template_body_parameter_ids)))
