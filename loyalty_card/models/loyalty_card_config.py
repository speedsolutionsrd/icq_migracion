from odoo import models, fields, api


class LoyaltyCardCumulaticeConfig(models.Model):
    _name = 'loyalty.card.cumulative.config'
    _description = "Configuration Cumulative for loyalty Cards"
    _inherit = ['mail.thread']

    name = fields.Many2one("product.category", string="Categoria", track_visibility="onchange")
    calc_type = fields.Selection([('value', 'Cantidad Fija'), ('percent', 'Porcentaje')],
                                 string="Tipo de Calculo",
                                 default="value", track_visibility="onchange")
    client_only = fields.Boolean(string="Propietario", track_visibility="onchange")
    amount = fields.Integer(string="Puntos que acumula", track_visibility="onchange")
    loyalty_point_time = fields.Integer(string="Validez", track_visibility="onchange")
    loyalty_point_time_period = fields.Selection([("days", "Dias"),
                                                  ("months", "Meses")], string="Periodo Validez",
                                                 track_visibility="onchange")


class LoyaltyConfig(models.TransientModel):
    _name = 'loyalty.config.settings'
    _description = "Loyalty Configuration"
    _inherit = ['res.config.settings']

    points_equivalent = fields.Integer(string="Points Equivalent")

    @api.model
    def set_points_equivalent(self):
        return self.env['ir.values'].sudo().set_default('loyalty.config.settings', 'points_equivalent',
                                                        self.points_equivalent)

    @api.model
    def get_points_equivalent(self):
        return self.env['ir.values'].sudo().get_default('loyalty.config.settings', 'points_equivalent')
