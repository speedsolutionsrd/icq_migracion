from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class LoyaltyCard(models.Model):
    _name = "loyalty.card"
    _description = "Loyalty Card Register"
    _inherit = ['mail.thread']

    name = fields.Char(string="Card No.", required=True, track_visibility="onchange")
    partner_id = fields.Many2one('res.partner', string="Partner", track_visibility="onchange")
    points = fields.Integer(string='Generated Points', compute="_compute_points")
    state = fields.Selection([('inactive', 'Inactive'), ('active', 'Active')], string="State", default="inactive",
                             track_visibility="onchange")
    loyalty_card_point_ids = fields.One2many('loyalty.card.point', 'name', string="Generated Points")

    @api.model
    def name_get(self):
        result = []
        for record in self:
            name = u'%s [%s]' % (record.name, record.points)
            result.append((record.id, name))
        return result

    @api.model
    def _compute_points(self):
        point_total = 0
        for point in self.env['loyalty.card.point'].search([('name', '=', self.id)]):
            if point.state == 'active':
                point_total += point.generated_points
        self.points = point_total

    _sql_constraints = [("unique_partner", "unique(partner_id)", "This partner has a Loyalty card assigned"),
                        ("unique_name", "unique(name)", "This Card number is duplicated")]
