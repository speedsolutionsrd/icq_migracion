from odoo import models, fields
from odoo.exceptions import Warning


class StockPickingProcess(models.TransientModel):
    _name = 'stock.picking.process'
    _description = 'Process Unpaid pickings'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    rental_cancel_code = fields.Char(string="Codigo de Cancelacion", required=True)
    order_amount = fields.Float(string="Due Amount", default=lambda self: self.env['stock.picking'].browse(
        self._context.get('active_id')).amount_due)
    f = fields.Char()

    def cancel_rental(self):
        if self.rental_cancel_code == self.employee_id.rental_cancel_code:
            self.env['stock.picking'].browse(self._context.get('active_id')).do_new_transfer()
        else:
            raise Warning("Clave Invalida")
