from odoo import models, fields


class WhatsappPromotion(models.Model):
    _name = 'whatsapp.promotion'
    _inherit = 'ir.attachment'

    name = fields.Char(string='Promotion', required=True)
    promotion_body = fields.Html(string="Details")

    def send_promotion(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Promotion',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'send.promotion.wizard',
            'target': 'new',
            'context': {"default_promotion_id": self.id}
        }
