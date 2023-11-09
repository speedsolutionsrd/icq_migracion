# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date, time


class SaleRental(models.Model):
    _inherit = 'sale.rental'

    tipo_cita = fields.Char(compute='_compute_tipo_cita', string='Tipo Cita', readonly=True)
    is_queued = fields.Boolean(string='Esta en Cola', compute="_compute_is_queued")
    queue_ids = fields.One2many('rentq.colas.vestidores', 'sale_rental_id')

    def _compute_is_queued(self):
        for rental in self:
            if rental.queue_ids.filtered(
                    lambda y: y.state_ticket != 'closed' and str(fields.Date.from_string(
                        y.date_start)) == str(fields.Date.today())):
                rental.is_queued = True
            else:
                rental.is_queued = False

    @api.model
    @api.depends('test_date', 'delivery_date')
    def _compute_tipo_cita(self):
        test_date = ""
        delivery_date = ""
        today = date.today().strftime('%Y-%m-%d')
        if self.test_date:
            test_date = self.test_date.split(' ')[0]
        if self.delivery_date:
            delivery_date = self.delivery_date.split(' ')[0]
        if test_date == delivery_date:
            self.tipo_cita = 'Probar y Entregar'
        elif test_date == today:
            self.tipo_cita = 'Probar'
        elif delivery_date == today:
            self.tipo_cita = 'Entregar'
