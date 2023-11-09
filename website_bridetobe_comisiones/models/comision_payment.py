from odoo import models, fields, api
from odoo.exceptions import Warning


class ComisionPayment(models.Model):
    _name = 'bridetobe.comision.payment'
    _description = ''
    _inherit = ['mail.thread']

    name = fields.Char(string="Payment Number", default="New", required=True, copy=False)
    # tarifa_comision_id = fields.Many2one('bridetobe.tarifa.comision', string="Departamento", required=True)

    start_date = fields.Date(string="Fecha Inicial")
    end_date = fields.Date(string="Fecha Final")

    comision_ids = fields.One2many('bridetobe.comision', 'comision_payment_id', string="Comisiones",
                                   on_delete="set null")
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('paid', 'Pagada')], string="State",
                             default="draft")
    payment_date = fields.Date(string="Fecha de Pago")
    employee_id = fields.Many2one('hr.employee', string="Prestador de Servicios", required=True)

    # @api.onchange('employee_id', 'start_date', 'end_date')
    # def update_comision_ids(self):
    #     self.comision_ids = self.get_comision_ids()

    # def get_comision_ids(self):
    #     comision_ids = self.env['bridetobe.comision'].search([('date', '>=', self.start_date),
    #                                                           ('date', '<=', self.end_date),
    #                                                           ('employee_id', '=', self.employee_id.id),
    #                                                           ('state', '!=', 'paid'),
    #                                                           ('comision_payment_id', 'in', [False, self.id])])
    #     self.comision_ids.write({'comision_payment_id': False})
    #     comision_ids.write({'comision_payment_id': self.id})
    #     return comision_ids

    def validate(self):
        if self.comision_ids:
            self.state = 'open'
        else:
            raise Warning('No existen comisiones para Validar')

    def process_payment(self):
        self.payment_date = fields.Date.today()
        self.state = 'paid'
        for comision in self.comision_ids:
            comision.state = 'paid'
            comision.payment_date = self.payment_date
            if not comision.paid_amount:
                comision.paid_amount = comision.amount

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bridetobe.comision.pago')
        return super(ComisionPayment, self).create(vals)

    # @api.multi
    # def write(self, vals):
    #     comision_id = super(ComisionPayment, self).write(vals)
    #     if len(vals.keys()) != 1:
    #         self.get_comision_ids()
    #     return comision_id

    def get_comision_ids(self):
        self.comision_ids.unlink()
        rental_ids = self.env['sale.rental'].search([('start_date', '>=', self.start_date),
                                                     ('start_date', '<=', self.end_date),
                                                     '|', '|', ('modista', '=', self.employee_id.id),
                                                     ('bordador_id', '=', self.employee_id.id),
                                                     ('seller_id', '=', self.employee_id.id),
                                                     ])
        rental_ids.filtered(
            lambda x: not x.comision_ids or x.comision_ids or x.comision_ids.filtered(
                lambda comision_id: comision_id.employee_id != self.employee_id)).create_comisiones(self.id,
                                                                                                    self.employee_id)

    def reset_draft(self):
        self.comision_ids.unlink()
        self.state = 'draft'

    @api.model
    def unlink(self):
        self.mapped('comision_ids').unlink()
        return super(ComisionPayment, self).unlink()
