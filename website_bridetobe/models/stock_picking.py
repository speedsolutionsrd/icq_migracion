from odoo import models, fields, api
from odoo.exceptions import UserError
import time
from ast import literal_eval


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    comments = fields.Text(string='Observaciones')
    picking_type_code = fields.Selection(related='picking_type_id.code')

    @api.model
    def _compute_amount_due(self):
        for picking in self:
            invoice_ids = self.env['account.invoice'].sudo().search([('origin', '=', picking.origin)])
            amount_due_total = 0.0
            invoiced = True
            for invoice_id in invoice_ids:
                amount_due_total += invoice_id.residual
                if invoice_id.state == 'draft':
                    invoiced = False
            picking.amount_due = amount_due_total

    @api.model
    def _get_product_barcodes(self):
        for picking in self:
            sale_rental_ids = self.env['sale.rental'].sudo().search([('start_order_id.name', '=', picking.origin)])
            picking.product_barcodes = ','.join(map(str,sale_rental_ids.mapped('rental_product_id').mapped('barcode')))

    amount_due = fields.Float(string="Pendiente de Pago", compute="_compute_amount_due")
    product_barcodes = fields.Char(compute="_get_product_barcodes", search="_search_product_barcodes")
    # invoiced = fields.Boolean(string="Facturado", compute="_compute_amount_due", store=True)
    invoiced = fields.Boolean(string="Facturado")

    @api.model
    def action_view_invoice(self):
        invoices = self.env['account.invoice'].search([('origin', '=', self.origin)])
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _search_product_barcodes(self, operator, value):
        filter_picking_ids = []
        query = """select sp.id from sale_order so
                        join sale_order_line sol on sol.order_id = so.id
                        join sale_rental sr on sr.start_order_line_id = sol.id
                        join product_template pt on pt.id = sr.rental_product_id
                        join product_product pp on pp.product_tmpl_id = pt.id
                        join stock_picking sp on sp.origin = so.name
                    where pp.barcode = '"""+value+"""' group by sp.id"""
        self.env.cr.execute(query)
        for picking in self.env.cr.fetchall():
            filter_picking_ids.append(picking[0])
        return [('id', 'in', filter_picking_ids)]

    def _change_rental_internal_state(self):
        related_order = self.env['sale.order'].search([('name', '=', self.origin)])
        sale_rental = self.env['sale.rental'].search(
            [('start_order_id', '=', related_order.id), ('out_picking_id', '=', self.id)])
        if sale_rental:
            sale_rental.state_internal = self.env.ref('website_bridetobe.internal_state_entregado')

    def _get_rentals(self):
        related_order = self.env['sale.order'].search([('name', '=', self.origin)])
        sale_rental = self.env['sale.rental'].search([('start_order_id', '=', related_order.id),
                                                      ('out_picking_id', '=', self.id),
                                                      ('state_internal', '!=',
                                                       self.env.ref('website_bridetobe.internal_state_entregado').id)])
        return sale_rental

    def process_transfer(self):
        sale_rental = self._get_rentals()
        if not sale_rental:
            if self.picking_type_code == 'outgoing':
                if self.amount_due:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Procesar Entrega',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.picking.process',
                        'view_id': self.env.ref('website_bridetobe.stock_picking_process_wizard_form').id,
                        'target': 'new',
                    }
                else:
                    return super(StockPicking, self).sudo().do_transfer()
            elif self.picking_type_code == 'incoming':
                if self.amount_due:
                    raise UserError("Existe un Monto Pendiente de pago por un valor de " + str(
                        self.amount_due) + " debe procesar el pago antes de continuar la Recepcion")
                else:
                    return super(StockPicking, self).sudo().do_transfer()
        else:
            sale_rental_ids = []
            for sale_rental_id in sale_rental:
                sale_rental_ids.append((0, 0, {'sale_rental_id': sale_rental_id.id,
                                               'sale_rental_product': sale_rental_id.rental_product_id.id,
                                               'entregar': False}))
            return {
                'type': 'ir.actions.act_window',
                'name': 'Articulos a Entregar',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.rental.entrega',
                'context': {"default_sale_rental_line_ids": sale_rental_ids,
                            "default_related_picking": self.id},
                'target': 'new',
            }

    def print_ticket(self):
        if self.picking_type_code == 'incoming':
            return self.env['posbox.print'].posbox_send_ticket('website_bridetobe.report_ticket_recepcion',
                                                               {'receipt': self, 'company': self.company_id})
