from odoo import models, fields
from odoo.exceptions import Warning


class SaleRentalCancel(models.TransientModel):
    _name = 'sale.rental.cancel'
    _description = 'Rental Cancelation'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=1)
    rental_cancel_code = fields.Char(string="Codigo de Cancelacion", required=1)
    f = fields.Char()

    def cancel_rental(self):
        if self.rental_cancel_code == self.employee_id.rental_cancel_code:
            self.env['sale.rental'].browse(self._context.get('active_id')).cancel_rental()
        else:
            raise Warning("Clave Invalida")