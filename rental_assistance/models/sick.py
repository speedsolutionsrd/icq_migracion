from odoo import models, fields, api


class Sick(models.Model):
    _name = 'sick.sick'

    type_indisposition = fields.Selection(
        [('available', 'Disponible'), ('sick', 'Indispuesto'), ('unavailable', 'No Asistio')],
        default="available", string='Tipo')
    employee_id = fields.Many2one('hr.employee', string='Asesor')
    reason = fields.Char(string="Razon")
