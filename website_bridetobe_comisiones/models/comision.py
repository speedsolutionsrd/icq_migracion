from odoo import models, fields, api


class Comision(models.Model):
    _name = "bridetobe.comision"
    _description = ""
    _order = "start_date asc"

    name = fields.Many2one('product.template', string="Vestido")
    code = fields.Char(related='rental_id.rental_product_id.barcode', string='Codigo Vestido')
    rental_id = fields.Many2one('sale.rental', string="Renta", required=True)
    start_date = fields.Date(related='rental_id.start_date', string='Fecha de inicio', store=True)
    comments = fields.Text(string="Comentarios")
    employee_id = fields.Many2one('hr.employee', string="Empleado")
    partner_id = fields.Many2one(related="rental_id.partner_id", string="Cliente")
    date = fields.Date(string="Fecha Creacion", default=fields.Date.today())
    state_internal = fields.Many2one('sale.rental.internal.state', string="Estado Cliente")
    amount = fields.Float(string="Monto a Pagar", track_visibility="onchange")
    tarifa_aplicada = fields.Many2one("bridetobe.tarifa.comision", string="Tarifa")
    comision_type = fields.Selection([("new", "Nueva"),
                                      ("change", "Cambio"),
                                      ("cancel", "Cancelacion")], string="Procedencia")
    state = fields.Selection([('pending', "Pendiente"), ('paid', "Pagada"), ('rejected', "Rechazada")], string="State",
                             default="pending", track_visibility="onchange")
    payment_date = fields.Date(string='Fecha de Pago', track_visibility="onchange")
    paid_amount = fields.Float(string='Monto Pagado', track_visibility="onchange")
    comision_payment_id = fields.Many2one('bridetobe.comision.payment', string="Pago", ondelete='set null')
    department_id = fields.Many2one(related='employee_id.department_id', string="Departamento")
    old_rented_product_id = fields.Many2one('product.template', string="Vestido Anterior")

    def _calc_amount(self, calc_type, amount, rental_id):
        if calc_type == "value":
            return amount
        elif calc_type == "percent":
            return (rental_id.start_order_line_id.price_subtotal * amount) / 100

    # @api.model
    # def create(self, vals):
    #     print(vals)
    #     return super(Comision, self).create(vals)

    #     tarifa_aplicada = self.env['bridetobe.tarifa.comision'].browse(vals.get('tarifa_aplicada'))
    #     rental_id = self.env['sale.rental'].browse(vals.get('rental_id'))
    #     vals['state_internal'] = rental_id.sudo().state_internal.id
    #
    #     if tarifa_aplicada.fix_comision:
    #         vals['amount'] = self._calc_amount(tarifa_aplicada.calc_type, tarifa_aplicada.amount, rental_id)
    #         vals['paid_amount'] = vals.get('amount')
    #         return super(Comision, self).create(vals)
    #     else:
    #         if not self.search([('employee_id', '=', vals.get('employee_id')),
    #                             ('name', '=', vals.get('name')),
    #                             ('state_internal', '=', rental_id.state_internal.id),
    #                             ('comision_type', '=', vals.get('comision_type'))]):
    #             for comision_line in tarifa_aplicada.comision_line:
    #                 if rental_id.sudo().state_internal == comision_line.internal_state:
    #                     if vals.get('comision_type') == 'new':
    #                         vals['amount'] = self._calc_amount(comision_line.calc_type, comision_line.new_amount,
    #                                                            rental_id)
    #                     if vals.get('comision_type') == 'change':
    #                         vals['amount'] = self._calc_amount(comision_line.calc_type, comision_line.change_amount,
    #                                                            rental_id)
    #                     if vals.get('comision_type') == 'cancel':
    #                         vals['amount'] = self._calc_amount(comision_line.calc_type, comision_line.cancel_amount,
    #                                                            rental_id)
    #                 if vals.get('amount') and vals.get('amount') != 0:
    #                     vals['paid_amount'] = vals.get('amount')
    #                     return super(Comision, self).create(vals)

    # def unlink(self):
    #     if self.env.context.get('params').get('model') == 'bridetobe.comision.payment':
    #         self.comision_payment_id = False
    #     elif self.env.context.get('params').get('model') == 'bridetobe.comision':
    #         return super(Comision, self).unlink()
