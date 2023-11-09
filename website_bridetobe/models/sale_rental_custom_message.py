from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError


class SaleRentalCustomMessage(models.Model):
    _name = 'sale.rental.custom.message'

    # name = fields.Char(string="Description", required=True)
    # available_model_id = fields.Many2one('sale.rental.custom.message.model', string="Available Models", required=True)
    # ir_model_id = fields.Many2one(related="available_model_id.ir_model_id", readonly=True)
    # ir_model_name = fields.Char(related="available_model_id.model_name", readonly=True)
    # ir_model_field_id = fields.Many2one("ir.model.fields", string="Evaluated Field", required=True,
    #                                     domain="[('model_id', '=', ir_model_id)]")
    # auto_send = fields.Boolean(string="Auto Send")
    # message_body = fields.Html(string="Message Body", required=True,
    #                            help="""
    #                            Valores que pueden ser utilizados para crear el mensaje
    #                            =======================================================
    #                            {0} : Cliente
    #                            {1} : Articulo
    #                            {2} : Estado
    #                            {3} : Modista
    #                            {4} : Orden Relacionada
    #                            {5} : Fecha de Prueba
    #                            {6} : Fecha Entrega
    #                            {7} : Dias transcurridos de Renta
    #                            {8} : Fecha Evento
    #                            {9} : Articulo Anterior
    #                            {10} : Fecha de Cambio de vestido
    #                            =======================================================
    #                            Ejemplo de uso: 
    #                             * Hola {0} el articulo {1} de su orden {4} a cambiado su
    #                               estado a {2} y esta siendo trabajado por la modista {3}  
    #                            """)

    name = fields.Char(string="Description", required=True)
    available_model_id = fields.Many2one('sale.rental.custom.message.model', string="Available Models", required=True)
    ir_model_id = fields.Many2one('ir.model', readonly=True)
    ir_model_name = fields.Char( readonly=True)
    # ir_model_field_id = fields.Many2one("ir.model.fields", string="Evaluated Field", required=True)
    auto_send = fields.Boolean(string="Auto Send")
    message_body = fields.Html(string="Message Body", required=True,
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


    # def get_message(self, object, key, auto_send=True):
    #     message_body = self.search([('ir_model_name', '=', object._name),
    #                                 ('ir_model_field_id.name', '=', key),
    #                                 ('auto_send', '=', auto_send)])
    #     return message_body

    @api.constrains("message_body")
    def _constraint_message_body(self):
        if len(tools.html2plaintext(self.message_body)) <= 1:
            raise ValidationError("Debe Especificar un cuerpo para el Mensaje")

    # _sql_constraints = [
    #     ('name_uniq', 'unique(name)', 'Existe otro registro con el mismo nombre'),
    #     ('ir_model_id_ir_model_field_id_uniq', 'unique(available_model_id,ir_model_field_id)', 'Mensaje Duplicado')
    # ]


class SaleRentalCustomMessageModel(models.Model):
    _name = 'sale.rental.custom.message.model'

    # name = fields.Char(related="ir_model_id.name", readonly=True)
    # model_name = fields.Char(related="ir_model_id.model", readonly=True)
    # ir_model_id = fields.Many2one('ir.model', string="Model", required=True, unique=False)
    # ir_model_field_ids = fields.One2many(related="ir_model_id.field_id", readonly=True)

    name = fields.Char(readonly=True)
    model_name = fields.Char(readonly=True)
    ir_model_id = fields.Many2one('ir.model', string="Model", required=True, unique=False)
    # ir_model_field_ids = fields.One2many(related="ir_model_id.field_id", readonly=True)

    # _sql_constraints = [('ir_model_id_uniq', 'unique(ir_model_id)', 'Modelo Duplicado')]
