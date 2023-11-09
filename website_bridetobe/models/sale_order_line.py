from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_order_line_procurement(group_id=group_id)
        if (self.product_id.rented_product_id and self.rental_type == 'new_rental'):
            product_id = self.env['product.product'].search(
                [('product_tmpl_id', '=', self.product_id.rented_product_id.id)])
            if product_id:
                res.update({
                    'product_id': product_id.id,
                })
        return res

    start_date = fields.Date(string='Start Date', readonly=False)
    end_date = fields.Date(string='End Date', readonly=False)
    extra_weeks = fields.Integer(related="order_id.extra_weeks")
    extra_weeks_dates = fields.Char(string="Extra Dates")
    exchange = fields.Boolean(related="order_id.exchange")
