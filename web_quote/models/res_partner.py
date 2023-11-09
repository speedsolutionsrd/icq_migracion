from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_code = fields.Char(string="Codigo de Cliente", help="Codigo de Cliente")

    @api.model
    def create(self, vals):
        if 'customer_code' in vals and vals.get('customer_code'):
            partner_id = self.search([('customer_code','=',vals.get('customer_code'))])
            if partner_id:
                raise ValidationError('Customer Code must be unique')
            else:
                return super(ResPartner, self).create(vals)
        else:
            return super(ResPartner, self).create(vals)
