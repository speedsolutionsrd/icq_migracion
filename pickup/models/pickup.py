from odoo import models, fields, api
from datetime import timedelta
from ast import literal_eval


class Pickup(models.Model):
    _name = 'pickup.pickup'
    _rec_name = "partner_id"
    _description = "Pickup"

    @api.model
    def _get_route(self):
        return [('state', '=', self.partner_id.state_id.id)]

    pickup_date = fields.Date(string='Date', default=fields.Date.today())
    estimated_date = fields.Date('Estimated date', default=fields.Date.context_today)
    status = fields.Selection([('pending', 'Pending'),
                               ('pickup', 'Pickup'),
                               ('complete', 'Complete'),
                               ('try', 'Pickup Attempt'),
                               ('canceled', 'Cancel')], string="Status", default="pending")
    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_address = fields.Char(related="partner_id.street", string='Address')
    route_id = fields.Many2one('pickup.route', string='Ruta')
    pickup_delivery_id = fields.Many2one("hr.employee", string="Pickup by")
    state_id = fields.Many2one(related="partner_id.state_id")
    delivery_id = fields.Many2one("hr.employee", string="Delivery assigned")

    def pickup_confirmation(self):
        self.status = 'complete'
        self.create_commission()

    def create_commission(self, fee=None):
        if self.status == 'complete':
            vals = {'pickup_id': self.id, 'delivery_id': self.pickup_delivery_id.id, 'amount': 250.00}
            self.env['pickup.commission'].create(vals)

    def write(self, vals):
        if vals.get('route_id'):
            self.status = 'pending'
        return super(Pickup, self).write(vals)
