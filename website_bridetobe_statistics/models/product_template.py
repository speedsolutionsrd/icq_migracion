from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    rental_ids = fields.One2many('sale.rental','rental_product_id',string="Rentas Relacionadas")