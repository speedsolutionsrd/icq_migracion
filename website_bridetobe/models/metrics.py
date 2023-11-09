from odoo import models, fields


class Metrics(models.Model):
    _name = 'bridetobe.metric'

    name = fields.Char(string="Medida")
    show_web = fields.Boolean(string="Visualizar en Formulario", default=False)

