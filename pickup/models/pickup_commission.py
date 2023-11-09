from odoo import models, fields, api


class PickupCommission(models.Model):
    _name = 'pickup.commission'
    _rec_name = "pickup_id"

    pickup_id = fields.Many2one('pickup.pickup', string="Pickup", required=True)
    delivery_id = fields.Many2one("hr.employee", string="Delivery")
    department_id = fields.Many2one(related='delivery_id.department_id', string="Departament")
    state_internal = fields.Selection(related="pickup_id.status", string="Pickup status")
    commission_date = fields.Date(string='Creation date', readonly=True, default=fields.Date.today())
    amount = fields.Float('Amount to payment')
    status = fields.Selection([('pending', "Pending"), ('paid', "Paid"), ('rejected', "Rejected")],
                              string="Status", default="pending", track_visibility="onchange")
    payment_date = fields.Date(string='Payment date', track_visibility="onchange")
    paid_amount = fields.Float(string='Paid Amount', track_visibility="onchange")
