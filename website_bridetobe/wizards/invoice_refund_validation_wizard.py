from odoo import models
from odoo.exceptions import Warning

class InvoiceRefundValidation(models.TransientModel):
    _name = 'invoice.refund.validation'
    _inherit = 'sale.rental.cancel'

    def process_cancel(self):
        if self.cancel_code == self.employee_id.rental_cancel_code:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice.refund',
                'target': 'new',
                'context': self.env.context
            }
        else:
            raise Warning("Clave Invalida")
