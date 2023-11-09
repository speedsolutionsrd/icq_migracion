from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    route_ids = fields.Many2many("pickup.route", 'route_employee_rel', 'employee_id', 'route_id', string="Routes")
