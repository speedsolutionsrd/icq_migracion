# -*- coding: utf-8 -*-
from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    seller_code = fields.Char(string="Codigo de Vendedor")
    rental_cancel_code = fields.Char(string="Codigo Cancelacion")

    _sql_constraints = [
        ('seller_code_uniq', 'unique(seller_code)', 'Este Codigo de Vendedor ya existe'),
    ]