# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.model
    # def _get_modista_domain(self):
    #     return [('department_id', '=', self.env.ref('website_bridetobe.modista').id)]

    def _get_default_internal_state(self):
        return self.state_internal.search([('sequence', '=', 1)])

    modista = fields.Many2one("hr.employee", string="Modista" """, domain=_get_modista_domain""")
    busto = fields.Float(string="Busto")
    cintura = fields.Float(string="Cintura")
    cadera = fields.Float(string="Cadera")
    event_place = fields.Char(string="Event Place")
    event_date = fields.Date(string="Event Date")
    state_internal = fields.Many2one('sale.rental.internal.state',
                                     string="Internal State",
                                     default=_get_default_internal_state)
    comments = fields.Text(string="Comments")
    falda = fields.Float(string="Largo de Falda")
    details = fields.Text(string="Details")
    seller_id = fields.Many2one('hr.employee', string="Vendedor")
    metric_ids = fields.One2many(related='partner_id.metric_ids')
    exchange = fields.Boolean(string="Es Intercambio?")
    extra_weeks = fields.Integer(string="Extra Weeks")

    @api.model
    def action_invoice_create(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_invoice_create()
        invoice_ids = self.env['account.invoice'].browse(res)
        for invoice_id in invoice_ids:
            invoice_id.event_date = self.event_date
            invoice_id.seller_id = self.seller_id
        for order in self:
            for line in order.order_line:
                if line.rental_type == 'new_rental':
                    line.product_id.is_rented = True
        return res

    @api.model
    def send_message(self):
        for order in self:
            state_internal = order.state_internal.search([('sale_order_state', '=', order.state)])
            if state_internal.message_send:
                order.state_internal = state_internal
                try:
                    order.message_ids.sudo().create({"subject": "Detalles de su Orden No." + order.name,
                                                    "subtype_id": 1,
                                                    "res_id": order.id,
                                                    "partner_ids": [(4, order.partner_id.id)],
                                                    "needaction_partner_ids": [(4, order.partner_id.id)],
                                                    "body": str(order.state_internal.message_body).format(
                                                        order.partner_id.name,
                                                        "",
                                                        order.state_internal.name,
                                                        order.modista.name,
                                                        order.name),
                                                    "record_name": order.name,
                                                    "date": datetime.today(),
                                                    "model": 'sale.order',
                                                    "author_id": order.env.user.id,
                                                    "message_type": "email",
                                                    "email_from": order.env.user.email})
                except (KeyError, IndexError):
                    _logger.error('El cuerpo del mensaje no esta Configurado correctamente')

    @api.model
    def write(self, vals):
        sale_order = super(SaleOrder, self).write(vals)
        if vals.get('state'):
            self.send_message()
        return sale_order

    @api.model
    def create(self, vals):
        sale_order = super(SaleOrder, self).create(vals)
        if vals.get('state'):
            sale_order.send_message()
        return sale_order

    @api.model
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            for line in order.order_line:
                if line.rental_type == 'new_rental':

                    parent_rental_id = self.env['sale.rental'].search(
                        [('start_order_line_id', '=', line.id), ('parent_rental_id', '=', False)])
                    if line.extra_weeks_dates:
                        extra_weeks_dates = eval(line.extra_weeks_dates)
                        for count in range(1, len(extra_weeks_dates)):
                            extra_week = extra_weeks_dates.get('event_date_' + str(count))
                            if extra_week:
                                self.env['sale.rental'].create({'start_order_line_id': line.id, 'start_date': extra_week,
                                                                'parent_rental_id': parent_rental_id.id})
        return res
