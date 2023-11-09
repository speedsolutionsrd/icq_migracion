from odoo import models, fields, api
from odoo.exceptions import UserError


class WhatsappMessage(models.Model):
    _name = 'whatsapp.send.message'
    _rec_name = "display_name"

    message = fields.Text(string="Message", required=1)
    partner_id = fields.Many2one('res.partner', string="Customer")
    mobile = fields.Char(string='Customer Whatsapp', required=1)
    display_name = fields.Char(string="name", compute="_compute_display_name")
    state = fields.Selection([('draft', 'Draft'),
                              ('fail', 'Fail'),
                              ('send', 'Send')], string="Status", default="draft")
    model = fields.Char(string="Related Model")
    model_id = fields.Integer(string="Related Model ID")

    def _compute_display_name(self):
        self.display_name = "%s (%s)" % (self.partner_id.name, self.mobile)

    @api.onchange('partner_id')
    def change_partner_id(self):
        self.mobile = self.partner_id.mobile

    def action_send(self, url=False, payload=False, request_type=False):
        raise UserError("Send Method not implemented")

    @api.model
    def default_get(self, fields):
        result = super(WhatsappMessage, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_id and active_model == 'res.partner':
            resource = self.env[active_model].browse(active_id)
            result['mobile'] = ','.join(resource.mapped('mobile'))
        return result
