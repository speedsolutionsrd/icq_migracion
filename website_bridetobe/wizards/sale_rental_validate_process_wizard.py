from odoo import models, fields
from odoo.exceptions import Warning


class SaleRentalValidateProcess(models.TransientModel):
    _name = 'sale.rental.validate.process'
    _inherit = 'sale.rental.cancel'

    def cancel_rental(self):
        if self.rental_cancel_code != self.employee_id.rental_cancel_code:
            raise Warning("Clave Invalida")

        #     print(self._context.get('vals'))
        #     # self.env['sale.rental'].browse(self._context.get('active_id')).cancel_rental()
        # else:
        #     raise Warning("Clave Invalida")