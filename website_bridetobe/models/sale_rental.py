# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.fields import Date

_logger = logging.getLogger(__name__)


class SaleRental(models.Model):
    _name = "sale.rental"
    _inherit = ['sale.rental', 'mail.thread']
    _order = 'delivery_date,state_internal'

    @api.model
    def _get_residual_time(self):
        for rental in self:
            if rental.delivery_date and rental.test_date:
                if datetime.today() > datetime.strptime(rental.test_date, DEFAULT_SERVER_DATETIME_FORMAT):
                    residual_datetime = datetime.strptime(rental.delivery_date,
                                                          DEFAULT_SERVER_DATETIME_FORMAT) - datetime.today()
                else:
                    residual_datetime = datetime.strptime(rental.test_date,
                                                          DEFAULT_SERVER_DATETIME_FORMAT) - datetime.today()
                residual_time = residual_datetime.total_seconds() // 3600
                residual_datetime.total_seconds() // 3600
                security_rental = self.env['ir.config_parameter'].get_param('sale_rental.rental_security_hours')#rental.start_order_id.company_id.security_rental
                if residual_time > security_rental and residual_time < (security_rental * 2) and rental.state in (
                        'ordered', 'pending'):
                    rental.alert_color = "yellow"
                elif residual_time <= security_rental and rental.state in ('ordered', 'pending'):
                    rental.alert_color = "crimson"

            if not rental.alert_color:
                rental.alert_color = rental.state_internal.state_color
            if rental.state == 'tested_out':
                rental.alert_color = 'yellow'

    @api.model
    def _get_modista_domain(self):
        return [('department_id', '=', self.env.ref('website_bridetobe.modista').id)]

    @api.model
    def _get_bordado_domain(self):
        return [('department_id', '=', self.env.ref('website_bridetobe.bordado').id)]

    @api.model
    def _get_default_internal_state(self):
        return self.state_internal.search([('sequence', '=', 1)])

    state_internal = fields.Many2one('sale.rental.internal.state',
                                     string="Estado Interno", ondelete="restrict",
                                     default=_get_default_internal_state)
    modista = fields.Many2one("hr.employee", string="Modista", domain=_get_modista_domain, track_visivility='onchange')
    bordador_id = fields.Many2one("hr.employee", string="Bordador", domain=_get_bordado_domain,
                                  track_visivility='onchange')
    event_place = fields.Char(related="start_order_id.event_place", string="Event Place")
    end_date = fields.Date(store=True)
    state = fields.Selection(selection_add=[('ordered', 'Sin Asignar'),
                                            ('pending', 'Pendiente de Prueba'),
                                            ('tested_out', 'Prueba y Entrega'),
                                            ('tested', 'Probado'),
                                            ('out', 'Entregado')], readonly=False,
                             track_visivility='onchange')
    alert_color = fields.Char(string="Alert Color",
                              compute="_get_residual_time")
    product_barcode = fields.Char(related="rental_product_id.barcode",
                                  readonly=True)
    delivery_date = fields.Datetime(string="Fecha Entrega")
    test_date = fields.Datetime(string="Fecha Prueba")
    comments = fields.Text(string="Comments")
    details = fields.Text(string="Details")
    rental_product_id = fields.Many2one('product.template', related="", string="Vestido", readonly=False,
                                        track_visibility="onchange")
    internal_comment = fields.Text(string="Nota Interna", track_visibility='onchange')
    receipt_render = fields.Text()
    receipt_url = fields.Char()
    seller_id = fields.Many2one(related='start_order_id.seller_id', string="Vendedor", store=True)
    current_days = fields.Integer(compute="_get_current_days", string="Dias Transcurridos")
    start_date = fields.Date(readonly=False, track_visibility="onchange",
                             string="Fecha Evento")
    metric_ids = fields.One2many(related='partner_id.metric_ids')
    old_rental_product_id = fields.Many2one('product.template', string="Vestido Viejo")
    change_rental_product_date = fields.Datetime(string="Fecha Cambio Vestido")
    extra_weeks = fields.Integer(related='start_order_id.extra_weeks')
    exchange = fields.Boolean("""related='start_order_line_id.exchange'""")
    parent_rental_id = fields.Many2one('sale.rental', string="Parent Rental")
    child_rental_ids = fields.One2many('sale.rental', 'parent_rental_id', string="Child Rentals")
    same_week_rentals = fields.Integer(string="MS", help="Vestidos en la misma Semana",
                                       compute="compute_same_week_rentals")
    has_product_change = fields.Boolean(string="Cambio", compute="compute_has_product_change")
    payment_status = fields.Selection([('pending', 'Pendiente'), ('parcial', 'Parcial'), ('complete', 'Pagado')],
                                      compute='_compute_payment_status', search='_search_payment_status',
                                      default="pending",
                                      string="Saldo", readonly=True)
    invoice_ids = fields.Many2many(related="start_order_id.invoice_ids")

    @api.model
    @api.depends('invoice_ids.state')
    def _compute_payment_status(self):
        for rental in self:
            invoices = rental.sudo().invoice_ids
            if invoices:
                state = invoices.mapped('state')
                residual = invoices.mapped('residual')
                total = invoices.mapped('amount_total')
                if 'paid' in state and not any(residual):
                    payment_status = 'complete'
                elif 'open' in state and sum(residual) != sum(total):
                    payment_status = 'parcial'
                else:
                    payment_status = 'pending'
                rental.payment_status = payment_status
            else:
                rental.payment_status = 'pending'

    def _search_payment_status(self, operator, value):
        action = self.env['ir.actions.act_window'].browse(self.env.context.get('params').get('action'))
        domain = action.domain.replace('context_today', 'datetime.utcnow').replace('datetime.timedelta', 'timedelta')
        recs = self.search(eval(domain)).filtered(lambda x: x.payment_status == value)
        return [('id', 'in', recs.ids)]

    def compute_has_product_change(self):
        for rental in self:
            if rental.old_rental_product_id:
                rental.has_product_change = True
            else:
                rental.has_product_change = False

    @api.depends('state')
    def next_state(self):
        if self.state_internal:
            last_state_sequence = max(
                a.sequence for a in self.state_internal.search([('sale_order_state', '=', False)]))
            if last_state_sequence != self.state_internal.sequence:
                next_sequence = min(
                    a.sequence for a in self.state_internal.search(
                        [('sequence', '>', self.state_internal.sequence), ('sale_order_state', '=', False)]))
                self.state_internal = self.state_internal.search([('sequence', '=', next_sequence)])
        else:
            state_ids = [a.sequence for a in self.state_internal.search([])]
            if state_ids:
                first_state = min(a.sequence for a in self.state_internal.search([]))
                self.state_internal = self.state_internal.search([('sequence', '=', first_state)])
            else:
                raise Warning('No existen estados Definidos')

    @api.model
    @api.depends(
        'start_order_line_id', 'extension_order_line_ids.end_date',
        'extension_order_line_ids.state', 'start_order_line_id.end_date')
    def _compute_display_name_field(self):
        for rental in self:
            rental.display_name = u'[%s] %s (%s)' % (
                rental.partner_id.name,
                rental.rented_product_id.name,
                rental._fields['state'].convert_to_export(rental.state, rental))

    def get_details(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.rental',
            'res_id': self.id,
            'context': self.env.context,
            'view_id': self.env.ref('sale_rental.sale_rental_form').id,
        }

    # @api.model
    # @api.depends(
    #     'start_order_line_id.order_id.state',
    #     'start_order_line_id.move_ids.state',
    #     'start_order_line_id.move_ids.move_dest_ids.state',
    #     'sell_order_line_ids.move_ids.state',
    # )
    # def _compute_procurement_and_move(self):
    #     for rental in self:
    #         procurement = False
    #         in_move = False
    #         out_move = False
    #         sell_procurement = False
    #         sell_move = False
    #         state = False
    #         if (rental.start_order_line_id):
    #             procurement = rental.start_order_line_id

    #             if procurement.move_ids:
    #                 for move in procurement.move_ids:
    #                     if move.move_dest_id:
    #                         out_move = move
    #                         in_move = move.move_dest_id
    #             if (rental.sell_order_line_ids and rental.sell_order_line_ids[0]):
    #                 sell_procurement = rental.sell_order_line_ids[0]
    #                 if sell_procurement.move_ids:
    #                     sell_move = sell_procurement.move_ids[0]
    #             state = 'ordered'
    #             if out_move and in_move:
    #                 if out_move.state == 'done':
    #                     state = 'out'
    #                 if out_move.state == 'done' and in_move.state == 'done':
    #                     state = 'in'
    #                 if (out_move.state == 'done' and in_move.state == 'cancel' and sell_procurement):
    #                     state = 'sell_progress'
    #                     if sell_move and sell_move.state == 'done':
    #                         state = 'sold'
    #             if rental.start_order_line_id.order_id.state == 'cancel':
    #                 state = 'cancel'
    #         rental.procurement_id = procurement
    #         rental.in_move_id = in_move
    #         rental.out_move_id = out_move
    #         rental.state = state
    #         rental.sell_procurement_id = sell_procurement
    #         rental.sell_move_id = sell_move
    #         if rental.state == 'in':
    #             rental.rental_product_id = False

    # @api.model
    # @api.depends(
    #     'start_order_line_id.order_id.state',
    #     'start_order_line_id.move_ids.state',
    #     'start_order_line_id.move_ids.move_dest_id.state',
    #     'sell_order_line_ids.move_ids.state',
    # )
    # def _compute_procurement_and_move(self):
    #     for rental in self:
    #         procurement = False
    #         in_move = False
    #         out_move = False
    #         sell_procurement = False
    #         sell_move = False
    #         state = False
    #         if (rental.start_order_line_id and rental.start_order_line_id.procurement_ids):
    #             procurement = rental.start_order_line_id.procurement_ids[0]

    #             if procurement.move_ids:
    #                 for move in procurement.move_ids:
    #                     if move.move_dest_id:
    #                         out_move = move
    #                         in_move = move.move_dest_id
    #             if (rental.sell_order_line_ids and rental.sell_order_line_ids[0].procurement_ids):
    #                 sell_procurement = rental.sell_order_line_ids[0].procurement_ids[0]
    #                 if sell_procurement.move_ids:
    #                     sell_move = sell_procurement.move_ids[0]
    #             state = 'ordered'
    #             if out_move and in_move:
    #                 if out_move.state == 'done':
    #                     state = 'out'
    #                 if out_move.state == 'done' and in_move.state == 'done':
    #                     state = 'in'
    #                 if (out_move.state == 'done' and in_move.state == 'cancel' and sell_procurement):
    #                     state = 'sell_progress'
    #                     if sell_move and sell_move.state == 'done':
    #                         state = 'sold'
    #             if rental.start_order_line_id.order_id.state == 'cancel':
    #                 state = 'cancel'
    #         rental.procurement_id = procurement
    #         rental.in_move_id = in_move
    #         rental.out_move_id = out_move
    #         rental.state = state
    #         rental.sell_procurement_id = sell_procurement
    #         rental.sell_move_id = sell_move
    #         if rental.state == 'in':
    #             rental.rental_product_id = False

    def post_message(self, message_body=False, parameters=False):
        if message_body:
            self.message_ids.create({
                "subject": "Detalles de su Renta" + self.start_order_id.name,
                "subtype_id": 1,
                "res_id": self.id,
                "partner_ids": [(4, self.partner_id.id)],
                "needaction_partner_ids": [(4, self.partner_id.id)],
                "body": message_body,
                "record_name": self.display_name,
                "date": datetime.today(),
                "model": 'sale.rental',
                "author_id": self.env.user.id,
                "message_type": "email",
                "email_from": self.env.user.email})
            return message_body
        return message_body

    @api.model
    def write(self, vals):
        for rental in self:
            if 'start_date' in vals and not self.env.user.has_group('sales_team.group_sale_manager'):
                raise ValidationError("No puede modificar la fecha del Evento")
            if 'rental_product_id' in vals and not self.env.user.has_group('sales_team.group_sale_manager'):
                raise ValidationError("No puede modificar Vestido")
            rental = rental.sudo()
            rental_product_id = rental.rental_product_id.rented_product_id.id
            if vals.get('start_date'):
                rental.start_order_line_id.write(
                    {'start_date': vals.get('start_date'), 'end_date': vals.get('start_date')})
                if rental.in_picking_id:
                    rental.in_picking_id.min_date = fields.Datetime.from_string(vals.get('start_date'))
                if rental.out_picking_id:
                    rental.out_picking_id.write({'min_date': fields.Datetime.from_string(vals.get('start_date'))})
            old_rental_product_id = rental.rental_product_id
            sale_rental = super(SaleRental, self).write(vals)
            message_body = False
            delivery_date = ""
            test_date = ""
            self_test_date = ""
            self_delivery_date = ""
            if rental.test_date:
                self_test_date = fields.Datetime.from_string(rental.test_date) + timedelta(hours=-4)
                test_date = datetime.strftime(self_test_date, '%d/%m/%Y %I:%M %p')

            if rental.delivery_date:
                self_delivery_date = fields.Datetime.from_string(rental.delivery_date) + timedelta(hours=-4)
                delivery_date = datetime.strftime(fields.Datetime.from_string(rental.delivery_date),
                                                  '%d/%m/%Y %I:%M %p')
            if vals.get('test_date') or vals.get('delivery_date'):
                if self_delivery_date and self_test_date:
                    if self_delivery_date.date() == self_test_date.date():
                        super(SaleRental, self).write({'state': 'tested_out'})

            message_data = [rental.partner_id.name,
                            rental.rental_product_id.barcode or ".",
                            rental.state_internal.name,
                            rental.modista.name,
                            rental.start_order_id.name,
                            test_date,
                            rental.delivery_date,
                            rental.current_days,
                            rental.start_date,
                            rental.old_rental_product_id.barcode]
            if rental.modista and vals.get('test_date'):
                if not vals.get('state'):
                    rental.state = 'pending'
                if not vals.get('state_internal'):
                    rental.state_internal = rental.env.ref('website_bridetobe.internal_state_ajuste').id
                if rental.state_internal.message_body:
                    message_body = rental.state_internal.message_body.format(*message_data)
            if message_body:
                rental.post_message(message_body, rental.state_internal, message_data)
            else:
                for key in vals.keys():
                    message = rental.env['sale.rental.custom.message'].get_message(self, key)
                    if message:
                        if rental.change_rental_product_date:
                            change_rental_product_date = fields.Datetime.from_string(
                                rental.change_rental_product_date) + timedelta(
                                hours=-4)
                        else:
                            change_rental_product_date = ""
                        message_data.append(change_rental_product_date)
                        message_body = message.message_body.format(*message_data)
                        rental.post_message(message_body, message, message_data)

            if 'rental_product_id' in vals:
                product_id = rental.env['product.product'].search(
                    [('product_tmpl_id', '=', rental.rental_product_id.id)],
                    limit=1)
                for move_line in rental.out_picking_id.move_lines:
                    if move_line.product_id.product_tmpl_id.id == rental_product_id:
                        move_line.product_id = rental.env['product.product'].search(
                            [('product_tmpl_id', '=', product_id.rented_product_id.id)], limit=1)
                for pack_operation in rental.out_picking_id.pack_operation_product_ids:
                    if pack_operation.product_id.product_tmpl_id.id == rental_product_id:
                        pack_operation.product_id = rental.env['product.product'].search(
                            [('product_tmpl_id', '=', product_id.rented_product_id.id)], limit=1)

                for move_line in rental.in_picking_id.move_lines:
                    if move_line.product_id.product_tmpl_id.id == rental_product_id:
                        move_line.product_id = rental.env['product.product'].search(
                            [('product_tmpl_id', '=', product_id.rented_product_id.id)], limit=1)
                for pack_operation in rental.in_picking_id.pack_operation_product_ids:
                    if pack_operation.product_id.product_tmpl_id.id == rental_product_id:
                        pack_operation.product_id = rental.env['product.product'].search(
                            [('product_tmpl_id', '=', product_id.rented_product_id.id)], limit=1)

                rental.start_order_line_id.procurement_ids[0].product_id = product_id
                rental.start_order_line_id.procurement_ids[0].name = rental.rental_product_id.name
                rental.start_order_line_id.product_id = product_id
                rental.start_order_line_id.name = rental.rental_product_id.name

                rental.old_rental_product_id = old_rental_product_id
                rental.change_rental_product_date = fields.Datetime.now()
            if rental.child_rental_ids:
                rental.child_rental_ids.write(vals)
        return True

    def get_availability(self, rental_product_id=False):
        date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
        date_start = date - timedelta(days=date.weekday())
        date_end = date + timedelta(days=7)
        product_availability = self.env['sale.rental'].sudo().search(
            [('rental_product_id', '=', rental_product_id or self.rental_product_id.id),
             '|', ('state', '!=', 'cancel'), ('state', '=', False),
             ('start_date', '<=', datetime.strftime(date_end, DEFAULT_SERVER_DATE_FORMAT)),
             ('start_date', '>=', datetime.strftime(date_start, DEFAULT_SERVER_DATE_FORMAT))])

        if product_availability:
            raise Warning("Este Articulo no esta disponible en esta Fecha")

    @api.onchange('rental_product_id')
    def onchange_rental_product_id(self):
        self.get_availability()
        # print
        # print(self.out_move_id.product_id)

    def print_receipt(self):
        receipt_url = self.env['ir.values'].get_default('stock.config.settings', 'label_printer_url') or "ZD410"
        # ============================
        self.sudo().next_state()
        out_picking_id = self.sudo().out_picking_id
        out_picking_id.sudo().force_assign()
        for picking_line in out_picking_id.pack_operation_product_ids:
            product_id = self.env['product.product'].search(
                [('product_tmpl_id', '=', self.rented_product_id.id)])
            if picking_line.product_id.id == product_id.id and picking_line.qty_done == 0:
                picking_line.sudo().write({'qty_done': 1.0})
        # ===============
        receipt_render = """^XA
				  ^FO0,20^A0N,50,62^FB500,0,0,C^FD{0}^FS
				  ^FO0,60^A0N,40,40^FB500,1,0,C^FD{2}^FS
				  ^FO30,100^BY4^BCN,100,Y,N,N^FD{1}^FS
				  ^XZ""".format(self.sudo().partner_id.company_id.name.encode('utf-8'),
                                self.sudo().rental_product_id.barcode,
                                self.sudo().partner_id.name.encode('utf-8'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Print Label',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'posbox.print',
            'context': {"default_receipt_url": receipt_url,
                        "default_receipt": receipt_render
                        },
            'view_id': self.env.ref('posbox_send.qztry_print_label_form').id,
            'target': 'new',
        }

    def _process_picking(self, picking_id, move_id):
        if len(picking_id.move_lines) > 1:
            move_id.state = 'draft'
            move_id.sudo().unlink()
        else:
            picking_id.action_cancel()

    def cancel_rental(self):
        for rental in self:
            if rental.parent_rental_id:
                rental = rental.parent_rental_id
            out_picking_id = rental.out_picking_id
            out_move_id = rental.out_move_id
            in_picking_id = rental.in_picking_id
            in_move_id = rental.in_move_id
            rental._process_picking(out_picking_id, out_move_id)
            rental._process_picking(in_picking_id, in_move_id)
            rental.start_order_id.action_done()
            rental.state = 'cancel'
            rental.state_internal = rental.env.ref('website_bridetobe.internal_state_cancelado')
            if not rental.parent_rental_id:
                message_data = [rental.partner_id.name,
                                rental.rental_product_id.barcode or ".",
                                rental.state_internal.name,
                                rental.modista.name,
                                rental.start_order_id.name,
                                ".",
                                rental.delivery_date]
                message_body = rental.state_internal.message_body.format(*message_data)
                rental.post_message(message_body, rental.state_internal, message_data)

    @api.onchange('delivery_date')
    def onchange_delivery_date(self):
        for rental_id in self:
            if rental_id.out_picking_id:
                rental_id.out_picking_id.min_date = rental_id.delivery_date

    @api.onchange('start_date')
    def onchange_start_date(self):
        self.test_date = False
        self.delivery_date = False

    @api.model
    def create(self, vals):
        start_order_line_id = self.env['sale.order.line'].browse(vals.get('start_order_line_id'))
        vals['rental_product_id'] = start_order_line_id.product_id.product_tmpl_id.id
        vals['comments'] = start_order_line_id.order_id.comments
        return super(SaleRental, self).create(vals)

    @api.model
    def _get_current_days(self):
        for rental in self:
            rental.current_days = (
                    datetime.today() - datetime.strptime(rental.start_date, DEFAULT_SERVER_DATE_FORMAT)).days

    @api.model
    def send_return_email(self):
        message_body = self.env['sale.rental.custom.message'].get_message(self, 'current_days', False)
        parameters = [self.partner_id.name,
                      self.rental_product_id.barcode or ".",
                      self.state_internal.name,
                      self.modista.name,
                      self.start_order_id.name,
                      ".",
                      self.delivery_date,
                      self.current_days,
                      self.start_date,
                      ".",
                      ""]
        return message_body, parameters

    def send_custom_message(self):

        local_context = dict(
            default_partner_id=self.partner_id.id,
            default_rental_id=self.id
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.rental.send.custom.message',
            'target': 'new',
            'context': local_context,
        }

    def action_view_invoice(self):
        return self.start_order_id.action_view_invoice()

    def process_delivery(self):
        self.out_picking_id.force_assign()
        return self.out_picking_id.process_transfer()

    def process_reception(self):
        self.in_picking_id.force_assign()
        return self.in_picking_id.process_transfer()

    def compute_same_week_rentals(self):
        for rental in self:
            if rental.start_date:
                date_start, date_end = self.get_event_week(rental.start_date)
                rental_ids = rental.sudo().search([('partner_id', '=', rental.partner_id.id),
                                                   ('start_date', '>=', date_start),
                                                   ('start_date', '<=', date_end)])
                rental.same_week_rentals = len(rental_ids) - 1

    def get_event_week(self, event_date):
        date = datetime.strptime(event_date, DEFAULT_SERVER_DATE_FORMAT)
        date_start = date - timedelta(days=date.weekday() + 3)
        date_end = date_start + timedelta(days=9)
        return datetime.strftime(date_start, DEFAULT_SERVER_DATE_FORMAT), \
            datetime.strftime(date_end, DEFAULT_SERVER_DATE_FORMAT)
