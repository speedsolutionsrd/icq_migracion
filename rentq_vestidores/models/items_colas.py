# -*- coding: utf-8 -*-
from odoo import models, fields, api

class itemsColas(models.Model):
    _name = 'items.colas'

    vestidores_ids = fields.Many2one("rentq.vestidores", string='id vestidores')
    colas_vestidores_ids = fields.Many2one("rentq.colas.vestidores", string='id colas_vestidores')
