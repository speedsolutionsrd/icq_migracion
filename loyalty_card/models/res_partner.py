from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_card_id = fields.Many2one('loyalty.card', string="Loyalty Card", track_visibility="onchange")
    loyalty_card_points = fields.Integer(related="loyalty_card_id.points", string="Generated Points")

    @api.model
    def write(self, vals):
        loyalty_card_id = self.loyalty_card_id
        partner_id = super(ResPartner, self).write(vals)
        if 'loyalty_card_id' in vals:
            if self.loyalty_card_id:
                self.loyalty_card_id.partner_id = self
                self.loyalty_card_id.state = "active"
            else:
                if loyalty_card_id.points > 0:
                    raise ValidationError(
                        "Loyalty Card has a %s points acumulated and can not be Removed" % loyalty_card_id.points)
                loyalty_card_id.partner_id = False
                loyalty_card_id.state = "inactive"
