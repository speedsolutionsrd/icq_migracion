# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class bridetobeColasVestidores(models.Model):
    _name = 'rentq.colas.vestidores'

    name = fields.Char(string='Codigo de Ticket', required=True)
    state_ticket = fields.Selection([('draft', 'Nuevo'),
                                     ('wait', 'Espera'),
                                     ('execute', 'Ejecutando'),
                                     ('closed', 'Cerrado')],
                                    string='Estatus del Ticket', default='draft', required=True)
    type_queue = fields.Selection([('test', 'Prueba'),
                                   ('making', 'Confección')],
                                  string='Tipo de Cola', default='test', required=True)
    encolado = fields.Boolean(string='Encolado', default=True)
    sale_rental_id = fields.Many2one("sale.rental", string="Alquiler de Venta")
    cliente_id = fields.Many2one("res.partner", string="Cliente")
    modista_id = fields.Many2one(related="sale_rental_id.modista", string="Modista")
    producto_ids = fields.Many2many("product.template", string="Productos")
    date_start = fields.Datetime(string='Fecha de asignacion')
    time_elapsed = fields.Char(compute='_compute_time_elapsed', string='tiempo transcurrido', readonly=True)
    vestidor_id = fields.Many2one('items.colas', compute='_compute_vestidor', string="Vestidor")
    notified = fields.Boolean(default=False)

    @api.model
    def _compute_vestidor(self):
        for item in self:
            item.vestidor_id = self.env['items.colas'].search([('colas_vestidores_ids', '=', item.id)], limit=1)

    @api.model
    @api.depends('date_start')
    def _compute_time_elapsed(self):
        time_elapsed = self.compute_time_elapsed()
        self.time_elapsed = str(time_elapsed) if time_elapsed else False

    def compute_time_elapsed(self):
        # if self.state_ticket == 'wait':
        date_start = self.date_start.split(' ')[1]
        today = datetime.today().strftime('%H:%M:%S')
        h1 = datetime.strptime(date_start, "%H:%M:%S")
        h2 = datetime.strptime(today, "%H:%M:%S")
        time_elapsed = abs(h2 - h1)
        return time_elapsed

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('rentq.colas.vestidores')
        return super(bridetobeColasVestidores, self).create(vals)

    def create_date_timezone(self):
        for cola in self:
            user_tz = pytz.timezone(self.create_uid.tz or self.env.user.tz or 'UTC')
            dt = pytz.timezone('UTC').localize(datetime.strptime(cola.create_date, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(user_tz)
            return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)