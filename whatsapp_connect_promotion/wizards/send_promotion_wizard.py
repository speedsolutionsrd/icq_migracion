from odoo import models, fields
from odoo.tools import html2plaintext


class SendPromotionWizard(models.TransientModel):
    _name = 'send.promotion.wizard'

    send_type = fields.Selection([('new', 'New Partner'),
                                  ('partner', 'Single Partner'),
                                  ('partner_lot', 'Custom Partner Group'),
                                  ('promotion_list', 'Specific List')], string="Send Type", required=True)
    partner_name = fields.Char(string="Partner Name")
    partner_mobile = fields.Char(string="Mobile")
    partner_id = fields.Many2one('res.partner', string="Partner")
    partner_ids = fields.Many2many('res.partner', string="Partners")
    promotion_list_id = fields.Many2one('whatsapp.promotion.list', string="Promotion List")
    promotion_id = fields.Many2one('whatsapp.promotion', string="Promotion")
    promotion_body = fields.Html(related="promotion_id.promotion_body", string="Details")

    def _send_promotion(self, partner_mobile, payload={}):
        if self.promotion_id.datas:
            payload.update({"phone": partner_mobile,
                            "body": "data:%s;base64,%s" % (self.promotion_id.mimetype, self.promotion_id.datas),
                            "filename": self.promotion_id.datas_fname,
                            "caption": html2plaintext(self.promotion_body)})
            self.env['whatsapp.send.message'].action_send(url="/sendFile", payload=payload)
        else:
            payload.update({"phone": partner_mobile,
                            "body": html2plaintext(self.promotion_body)})
            self.env['whatsapp.send.message'].action_send(payload=payload)

    def send_promotion(self):
        if self.send_type == 'new':
            self.partner_id.create({'name': self.partner_name,
                                    'mobile': self.partner_mobile})
            self._send_promotion(self.partner_mobile)
        elif self.send_type == 'partner':
            self._send_promotion(self.partner_id.mobile, {'partner_id': self.partner_id.id})
        elif self.send_type == 'partner_lot':
            for partner_id in self.partner_ids:
                self._send_promotion(partner_id.mobile, {'partner_id': partner_id.id})
        elif self.send_type == 'promotion_list':
            for partner_id in self.promotion_list_id.partner_ids:
                self._send_promotion(partner_id.mobile, {'partner_id': partner_id.id})
