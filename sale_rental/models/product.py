# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Link rental service -> rented HW product
    rented_product_id = fields.Many2one(
        'product.template', string='Related Rented Product',
        domain=[('type', 'in', ('product', 'consu'))])
    # Link rented HW product -> rental service
    rental_service_ids = fields.One2many(
        'product.template', 'rented_product_id',
        string='Related Rental Services')

    @api.model
    @api.constrains('rented_product_id', 'must_have_dates', 'type', 'uom_id')
    def _check_rental(self):
        if self.rented_product_id and self.type != 'service':
            raise ValidationError(_(
                "The rental product '%s' must be of type 'Service'.")
                % self.name)
        if self.rented_product_id and not self.must_have_dates:
            raise ValidationError(_(
                "The rental product '%s' must have the option "
                "'Must Have Start and End Dates' checked.")
                % self.name)
        # In the future, we would like to support all time UoMs
        # but it is more complex and requires additionnal developments
        day_uom = self.env.ref('uom.product_uom_day')
        if self.rented_product_id and self.uom_id != day_uom:
            raise ValidationError(_(
                "The unit of measure of the rental product '%s' must "
                "be 'Day'.") % self.name)

class ProductProduct(models.Model):
    _inherit = 'product.product'
    def _need_procurement(self):
        # Missing self.ensure_model() in the native code !
        res = super(ProductProduct, self)._need_procurement()
        if not res:
            for product in self:
                if product.type == 'service' and product.rented_product_id:
                    return True
        # TODO find a replacement for soline.rental_type == 'new_rental')
        return res
