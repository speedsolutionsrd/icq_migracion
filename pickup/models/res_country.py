from odoo import api, fields, models


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    pickup = fields.Boolean("Servicio Recogida", compute='_compute_pickup')
    route_id = fields.One2many('pickup.route', 'state_id')

    @api.depends('route_id')
    def _compute_pickup(self):
        for state in self:
            if state.route_id:
                state.pickup = True
            else:
                state.pickup = False
