from odoo import models, fields, api


class Assistance(models.Model):
    _name = 'assistance.assistance'
    _rec_name = 'assessor'

    sequence = fields.Integer()
    employee_id = fields.Many2one('hr.employee', string='Asesor')
    assessor = fields.Char(related='employee_id.name', readonly=True)
