from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    security_rental = fields.Integer(string="Rental Security Hours", default=0.0)
    rental_conditions = fields.Html(string="Condiciones de Renta")