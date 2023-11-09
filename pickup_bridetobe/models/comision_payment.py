from odoo import models, fields, api
from odoo.exceptions import Warning


class ComisionPayment(models.Model):
    _inherit = ['bridetobe.comision.payment']

    pickup_comision_ids = fields.One2many('pickup.commission', 'comision_payment_id', string="Comisiones",
                                          on_delete="set null")

    def validate(self):
        if self.comision_ids or self.pickup_comision_ids:
            self.state = 'open'
        else:
            raise Warning('No existen comisiones para Validar')

    def process_payment(self):
        if self.pickup_comision_ids:
            self.payment_date = fields.Date.today()
            self.state = 'paid'
            for comision in self.pickup_comision_ids:
                comision.status = 'paid'
                comision.payment_date = self.payment_date
                if not comision.paid_amount:
                    comision.paid_amount = comision.amount
        else:
            super(ComisionPayment, self).process_payment()

    def get_comision_ids(self):
        if self.employee_id.department_id.id == self.env.ref('pickup.delivery').id:
            commission_ids = self.env['pickup.commission'].search(
                [('commission_date', '>=', self.start_date), ('commission_date', '<=', self.end_date),
                 ('delivery_id', '=', self.employee_id.id), ('status', '!=', 'paid')])
            for comision in commission_ids:
                comision.write({'comision_payment_id': self.id})
        else:
            super(ComisionPayment, self).get_comision_ids()

    def reset_draft(self):
        if self.pickup_comision_ids:
            self.pickup_comision_ids.unlink()
            self.state = 'draft'
        else:
            super(ComisionPayment, self).reset_draft()

    @api.model
    def unlink(self):
        if self.pickup_comision_ids:
            self.mapped('pickup_comision_ids').unlink()
            return super(ComisionPayment, self).unlink()
        else:
            super(ComisionPayment, self).unlink()
