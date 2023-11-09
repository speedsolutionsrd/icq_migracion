from odoo import models, fields, api


class PickupCommission(models.Model):
    _inherit = 'pickup.commission'

    comision_payment_id = fields.Many2one('bridetobe.comision.payment', string="Pago", ondelete='set null')
