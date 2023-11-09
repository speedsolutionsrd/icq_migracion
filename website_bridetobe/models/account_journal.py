from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    restricted = fields.Boolean(string="Restrict User", compute="is_restricted")
    restricted_groups = fields.Many2many("res.groups", string="grupos restringidos")

    @api.model
    def is_restricted(self):
        for group in self.mapped("restricted_groups"):
            self.restricted = self.env.user in group.users








