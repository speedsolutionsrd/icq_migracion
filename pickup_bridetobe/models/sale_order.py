# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pickup = fields.Boolean(string="Recogida")
