from odoo import models, fields, api


class PickupRoute(models.Model):
    _name = 'pickup.route'

    name = fields.Char('Route')

    @api.model
    def _get_delivery_domain(self):
        return [('department_id', '=', self.env.ref('pickup.delivery').id)]

    # delivery_ids = fields.One2many("hr.employee", 'route_id', string="Delivery", domain=_get_delivery_domain)
    delivery_ids = fields.Many2many("hr.employee", 'route_employee_rel','route_id', 'employee_id', string="Delivery", domain=_get_delivery_domain)
    state_id = fields.Many2one('res.country.state', string="State", required=True)
