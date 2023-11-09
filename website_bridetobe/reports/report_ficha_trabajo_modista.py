from odoo import models, api, _, fields
from odoo.exceptions import UserError


class ReportFichaTrabajoModista(models.TransientModel):
    _name = 'report.bridetobe.ficha_trabajo_modista'

    @api.model
    def _get_modista_domain(self):
        return [('department_id', '=', self.env.ref('website_bridetobe.modista').id)]

    modista_ids = fields.Many2many('hr.employee', string="Modistas", domain=_get_modista_domain)
    start_date = fields.Date(string="Fecha Inicial", required=True)
    end_date = fields.Date(string="Fecha Final", required=True)

    def get_rentals(self, modista_id=False):
        if modista_id:
            sale_rental_ids = self.env['sale.rental'].search(
                [('test_date', '>=', self.start_date),
                 ('test_date', '<=', self.end_date),
                 ('modista', '=', modista_id.id),
                 ('state','!=','cancel')
                 ])
        else:
            sale_rental_ids = self.env['sale.rental'].search(
                [('test_date', '>=', self.start_date),
                 ('test_date', '<=', self.end_date),
                 ('state','!=','cancel')])
        return sale_rental_ids

    def get_modistas(self):
        return self.env['hr.employee'].search(
            [('department_id', '=', self.env.ref('website_bridetobe.modista').id)])

    def _print_report(self, data):
        raise UserError(_('Not implemented.'))

    @api.model
    def check_report(self):
        return self.env['report'].get_action(self, 'website_bridetobe.template_ficha_trabajo_modista')