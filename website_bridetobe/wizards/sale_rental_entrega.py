from odoo import models, fields, api

class SaleRentalEntrega(models.TransientModel):
    _name = "sale.rental.entrega"
    _description = "Seleccion de Articulos a entregar"

    sale_rental_line_ids = fields.One2many('sale.rental.entrega.line', 'sale_rental_entrega_id',
                                           string="Lineas de Entrega")
    related_picking = fields.Many2one('stock.picking', string="Picking")

    def process(self):
        for sale_rental_line_id in self.sale_rental_line_ids:
            sale_rental_line_id.sale_rental_id.state_internal = self.env.ref(
                'website_bridetobe.internal_state_entregado')
            self.related_picking.sudo().force_assign()
            related_picking_pack_operation = self.env['stock.pack.operation'].search(
                [('picking_id', '=', self.related_picking.id),
                 ('product_id', 'in', self.env['product.product'].search(
                     [('product_tmpl_id', '=', sale_rental_line_id.sale_rental_product.rented_product_id.id)]).ids)])
            if related_picking_pack_operation:
                related_picking_pack_operation.qty_done = related_picking_pack_operation.product_qty
        self.related_picking.sudo().do_new_transfer()


class SaleRentalEntregadoLine(models.TransientModel):
    _name = "sale.rental.entrega.line"
    _description = "Articulos a entregar"

    sale_rental_id = fields.Many2one('sale.rental', string="Renta")
    sale_rental_product = fields.Many2one('product.template', string='Vestido')
    entregar = fields.Boolean(string="Entregar")
    sale_rental_entrega_id = fields.Many2one("sale.rental.entrega", string="Rental Entrega")
