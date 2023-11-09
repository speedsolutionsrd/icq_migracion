from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pickup = fields.Boolean(related="order_id.pickup")
