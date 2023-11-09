from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class LoyaltyCardPoint(models.Model):
    _name = "loyalty.card.point"
    _description = "Points Generation redister for Loyalty Cards"
    _inherit = ['mail.thread']

    name = fields.Many2one("loyalty.card", string="Loyalty Card", required=True)
    generated_points = fields.Integer(string="Generated Points", required=True)
    generation_date = fields.Date(string="Date of Generation")
    expiration_date = fields.Date(string="Date of Expiration")
    loyalty_config = fields.Many2one('loyalty.card.cumulative.config', string="Category Applied")
    product_id = fields.Many2one('product.product', string="Related Product")
    invoice_id = fields.Many2one('account.invoice', string="Related Invoice", required=True)
    state = fields.Selection([("active", "Active"),
                              ("inactive", "Inactive")], string="State", compute="_compute_state")

    @api.model
    def _compute_state(self):
        if self.generated_points > 0 and self.expiration_date and datetime.strptime(self.expiration_date,
                                                                                    DEFAULT_SERVER_DATE_FORMAT) < datetime.today():
            self.state = 'inactive'
        else:
            self.state = 'active'

    _sql_constraints = [("unique_point", "unique(name,invoice_id,product_id)", "Duplicated point register")]
