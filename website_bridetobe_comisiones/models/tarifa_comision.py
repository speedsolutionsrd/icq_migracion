from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TarifaComision(models.Model):
    _name = 'bridetobe.tarifa.comision'
    _description = 'Tarifas de comisiones'
    _inherit = ["mail.thread"]

    name = fields.Many2one('hr.department', string="Departamento", required=True,
                           help="Departamento relacionado a la comision", track_visibility="onchange")
    category_id = fields.Many2one('product.category', string="Categoria", help="Categoria de productos Relacionada",
                                  track_visibility="onchange")
    comision_line = fields.One2many('bridetobe.tarifa.comision.line', 'comision_id', string="Montos de Comision",
                                    track_visibility="onchange")
    amount = fields.Float(string="Comision", track_visibility="onchange")
    fix_comision = fields.Boolean(string="Comision Fija", default=False, track_visibility="onchange")
    calc_type = fields.Selection([('value', 'Cantidad Fija'), ('percent', 'Porcentaje')], string="Tipo de Calculo",
                                 default="value", track_visibility="onchange")
    payment_frequency = fields.Selection([('weekly', 'Semanal'),
                                          ('biweekly', 'Quincenal'),
                                          ('monthly', 'Mensual')], string="Frecuencia de Pago", required=False)

    @api.constrains('amount')
    def _check_amount(self):
        if self.fix_comision and self.amount == 0:
            raise ValidationError("El monto de la comision Debe ser difente de 0")

    _sql_constraints = [
        ('tarifa_unica', 'unique(name,category_id)', 'Tarifa ya existe para este Departamento'),
        ('unique_name', 'unique(name)', 'Tarifa ya existe')
    ]


class ComisionLine(models.Model):
    _name = 'bridetobe.tarifa.comision.line'
    _description = 'Lineas de Comision'
    _inherit = ["mail.thread"]

    comision_id = fields.Many2one('bridetobe.tarifa.comision', string="Comision", track_visibility="onchange")
    internal_state = fields.Many2one('sale.rental.internal.state', string="Status", required=True,
                                     track_visibility="onchange")
    new_amount = fields.Float(string="Nueva", required=False, track_visibility="onchange")
    change_amount = fields.Float(string="Cambio", track_visibility="onchange")
    cancel_amount = fields.Float(string="Cancelacion", track_visibility="onchange")
    invoice_state = fields.Selection([(0, 'Sin Validar'),
                                      (1, 'Validada')], string="Estado Factura")
    invoice_balance = fields.Selection([(0, 'Con Balance'),
                                        (1, 'Pagada')], string="Balance")
    change = fields.Boolean(string="Es Cambio?")

    amount = fields.Float(string="Monto a Pagar")

    calc_type = fields.Selection([('value', 'Cantidad Fija'), ('percent', 'Porcentaje')], string="Tipo de Calculo",
                                 default="value", required=True, track_visibility="onchange")

    @api.constrains('comision_id', 'internal_state', 'invoice_state', 'invoice_balance', 'change')
    def check_duplicate(self):
        line_ids = self.search([('id', '!=', self.id),
                                ('comision_id', '=', self.comision_id.id),
                                ('internal_state', '=', self.internal_state.id),
                                ('invoice_state', '=', self.invoice_state),
                                ('invoice_balance', '=', self.invoice_balance),
                                ('change', '=', self.change)])
        if line_ids:
            raise ValidationError("Comision Duplicada")
    # _sql_constraints = [
    #     ('tarifa_line_unica', 'unique()', 'Comision Duplicada'),
    # ]

    # @api.constrains('new_amount')
    # def _check_amount(self):
    #     if self.new_amount == 0:
    #         raise ValidationError(
    #             "El monto de la comision en el estatus %s Debe ser difente de 0" % (self.internal_state))
