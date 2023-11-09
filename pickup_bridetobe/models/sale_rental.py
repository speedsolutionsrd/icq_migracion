# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.fields import Date
from datetime import timedelta
_logger = logging.getLogger(__name__)


class SaleRental(models.Model):
    _inherit = 'sale.rental'

    pickup = fields.Boolean(related="start_order_line_id.pickup")

    def create(self, vals):
        rental_id = super(SaleRental, self).create(vals)
        if rental_id.pickup:
            self.env['pickup.pickup'].create({'rental_id': rental_id.id})
        return rental_id
