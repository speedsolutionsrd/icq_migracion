from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleRental(models.Model):
    _inherit = 'sale.rental'

    @api.model
    def _compute_delivery_done_days(self):
        if self.delivery_done_date and self.delivery_date:
            delivery_done_days = (datetime.strptime(self.delivery_done_date, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(self.delivery_date, DEFAULT_SERVER_DATETIME_FORMAT))
            self.delivery_done_days = delivery_done_days.days
        else:
            self.delivery_done_days = False

    delivery_done_date = fields.Datetime(related="out_picking_id.date_done", store=True)
    delivery_done_days = fields.Integer(string="Delivery Days", compute="_compute_delivery_done_days", store=True)