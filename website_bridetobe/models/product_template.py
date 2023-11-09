from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    @api.depends('name')
    def _get_short_name(self):
        for product in self:
            product.label_name = product.name[:28]

    is_rented = fields.Boolean(string="Is Rented")
    label_name = fields.Char(string="Short Name", compute=_get_short_name)
    rental_code = fields.Char(string='Rental Barcode')
    type = fields.Selection(default='product')

    @api.model
    def create(self, vals):
        product = super(ProductTemplate, self).create(vals)
        day_uom_id = self.env.ref('uom.product_uom_day').id
        if vals.get('type') != 'service':
            rented_vals = {
                'type': 'service',
                'sale_ok': True,
                'purchase_ok': False,
                'uom_id': day_uom_id,
                'uom_po_id': day_uom_id,
                'list_price': product.list_price,
                'name': 'Rental of ' + product.name,
                'default_code': product.rental_code,
                'barcode': product.rental_code,
                'rented_product_id': product.id,
                'must_have_dates': True,
                'categ_id': product.categ_id.id,
                'invoice_policy': 'order',
                # 'image': product.image
            }
            rental = super(ProductTemplate, self).create(rented_vals)
        return product

    def write(self, vals):
        product = super(ProductTemplate, self).write(vals)
        count = 0
        if 'image_medium' in vals:
            for rental_service_id in self.rental_service_ids:
                rental_service_id.image_medium = vals.get('image_medium')
        for rental_service_id in self.rental_service_ids:
            rental_service_id.update({'name': 'Rental of ' + vals.get('name', self.name),
                                      'list_price':vals.get('list_price', self.list_price),
                                      'categ_id': vals.get('categ_id', self.categ_id)})
        if len(self.rental_service_ids) == 1:
            self.rental_service_ids.barcode = vals.get('rental_code', self.rental_code)
            self.rental_service_ids.default_code = vals.get('rental_code', self.rental_code)
        return product

        # def print_report_simple_label_receipt(self):
        #     printer_url = self.env['stock.config.settings'].search([], order="id desc",
        #                                                            limit=1).label_printer_url
        #     self.env['posbox.print'].posbox_send_ticket('website_bridetobe.report_simple_label_receipt', {'product': self},
        #                                                 printer_url)


class CreateRentalProduct(models.TransientModel):
    _inherit = 'create.rental.product'

    @api.model
    def _prepare_rental_product(self):
        assert self.env.context.get('active_model') == 'product.template', \
            'Wrong underlying model, should be product.template'
        hw_product_id = self.env.context.get('active_id')
        assert hw_product_id, 'Active ID is not set'
        pp_obj = self.env['product.template']
        hw_product = pp_obj.browse(hw_product_id)
        day_uom_id = self.env.ref('uom.product_uom_day').id

        vals = {
            'type': 'service',
            'sale_ok': True,
            'purchase_ok': False,
            'uom_id': day_uom_id,
            'uom_po_id': day_uom_id,
            'list_price': self.sale_price_per_day,
            'name': self.name,
            'default_code': self.default_code,
            'barcode': self.default_code,
            'rented_product_id': hw_product_id,
            'must_have_dates': True,
            'categ_id': self.categ_id.id,
            'invoice_policy': 'order',
        }
        if self.copy_image:
            vals['image'] = hw_product.image
        return vals
