from odoo import models, fields, api


class PickupAttempt(models.Model):
    _name = 'pickup.attempt'
    _rec_name = 'pickup_id'

    pickup_id = fields.Many2one('pickup.pickup', string='Pickup')
    partner_id = fields.Many2one(related="pickup_id.partner_id", string='Customer')
    delivery_id = fields.Many2one("hr.employee", string="Delivery")
    reason = fields.Char(string="Reason")
    pickup_date = fields.Date(string='Date', readonly=True, default=fields.Date.context_today)
    status = fields.Selection([('pickup', 'Picked up'),
                               ('try', 'Pickup Attempt')], string="Status")

    def create(self, vals):
        attempt = super(PickupAttempt, self).create(vals)
        if attempt.status == 'pickup':
            attempt.pickup_id.write({'status': attempt.status, 'pickup_delivery_id': attempt.delivery_id.id})
        else:
            attempt.pickup_id.write({'status': attempt.status})
        return attempt
