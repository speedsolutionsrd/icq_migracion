# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    busto = fields.Float(string="Busto")
    cintura = fields.Float(string="Cintura")
    cadera = fields.Float(string="Cadera")
    falda = fields.Float(string="Largo de Falda")
    espalda = fields.Float(string="Espalda")
    talle_delantero = fields.Float(string="Talle Delantero")
    altura_busto = fields.Float(string="Altura Busto")
    separacion_busto = fields.Float(string="Separacion Busto")
    talle_trasero = fields.Float(string="Talle Trasero")
    largo_manga = fields.Float(string="Largo Manga")
    ancho_manga = fields.Float(string="Ancho Manga")
    metric_ids = fields.One2many('res.partner.metric', 'partner_id', string="Medidas")

    @api.onchange('name')
    @api.depends('name')
    def upper_name(self):
        self.name = self.name.upper() if self.name else False


class ConfectionMetric(models.Model):
    _name = 'res.partner.metric'
    _rec_name = "metric_id"

    metric_id = fields.Many2one('bridetobe.metric', string="Descripcion", required=True)
    partner_id = fields.Many2one('res.partner')
    amount = fields.Float(string="Medida", required=True)

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount <= 0:
            raise ValidationError("Las Medidas deben ser mayor que 0.0")

    _sql_constraints = [
        ('metric_uniq', 'unique(metric_id,partner_id)', 'Medida ya existe'),
    ]
