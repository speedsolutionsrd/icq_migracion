from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleRentalCustomMessage(models.Model):
    _inherit = 'sale.rental.custom.message'

    whatsapp_template_id = fields.Many2one('meta.connect.whatsapp.template', string="Whatsapp Template")
    whatsapp_template_body = fields.Text(related="whatsapp_template_id.body")
    whatsapp_template_body_parameter_ids = fields.One2many('sale.rental.custom.message.parameter', 'message_id',
                                                           string="Parameters")
    parameter_count = fields.Integer(related='whatsapp_template_id.parameter_count')

    @api.constrains('whatsapp_template_body_parameter_ids', 'whatsapp_template_id')
    def _check_parameter_ids(self):
        if self.parameter_count == 0:
            self.whatsapp_template_body_parameter_ids.unlink()
        if len(self.whatsapp_template_body_parameter_ids) != self.parameter_count:
            raise ValidationError(
                'Se requieren %s parametros para este template usted agrego %s' % (
                self.sudo().whatsapp_template_id.parameter_count, len(self.whatsapp_template_body_parameter_ids)))


class SaleRentalCustomMessageParameters(models.Model):
    _name = "sale.rental.custom.message.parameter"

    name = fields.Integer(string="Parameter", required=True)
    message_id = fields.Many2one('sale.rental.custom.message', string="Message")
    state_id = fields.Many2one('sale.rental.internal.state', string="Message")
    value = fields.Selection([('0', 'Cliente'),
                              ('1', 'Articulo'),
                              ('2', 'Estado'),
                              ('3', 'Modista'),
                              ('4', 'Orden Relacionada'),
                              ('5', 'Fecha de Prueba'),
                              ('6', 'Fecha Entrega'),
                              ('7', 'Dias transcurridos de Renta'),
                              ('8', 'Fecha Evento'),
                              ('9', 'Articulo Anterior'),
                              ('10', 'Fecha de Cambio de vestido')], required=True, string="Data",
                             help="""
                               Valores que pueden ser utilizados para crear el mensaje
                               =======================================================
                               {0} : Cliente
                               {1} : Articulo
                               {2} : Estado
                               {3} : Modista
                               {4} : Orden Relacionada
                               {5} : Fecha de Prueba
                               {6} : Fecha Entrega
                               {7} : Dias transcurridos de Renta
                               {8} : Fecha Evento
                               {9} : Articulo Anterior
                               {10} : Fecha de Cambio de vestido
                               =======================================================
                               Ejemplo de uso: 
                                * Hola {0} el articulo {1} de su orden {4} a cambiado su
                                  estado a {2} y esta siendo trabajado por la modista {3}  
                               """)


class SaleRentalCustomMessageParametersConfeccion(models.Model):
    _name = "sale.rental.custom.message.parameter.confeccion"
    _inherit = "sale.rental.custom.message.parameter"

    value = fields.Selection([('0', 'Cliente'),
                              ('1', 'Articulo'),
                              ('2', 'Estado'),
                              ('3', 'Modista'),
                              ('4', 'Orden Relacionada'),
                              ('5', 'Fecha de Prueba'),
                              ('6', 'Fecha Entrega')], required=True, string="Data",
                             help="""
                               Valores que pueden ser utilizados para crear el mensaje
                               =======================================================
                               {0} : Cliente
                               {1} : Articulo
                               {2} : Estado
                               {3} : Modista
                               {4} : Orden Relacionada
                               {5} : Fecha de Prueba
                               {6} : Fecha Entrega
                               =======================================================
                               Ejemplo de uso: 
                                * Hola {0} el articulo {1} de su orden {4} a cambiado su
                                  estado a {2} y esta siendo trabajado por la modista {3}  
                               """)
