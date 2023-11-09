from odoo import models, fields


class WhatsappPromotionList(models.Model):
    _name = 'whatsapp.promotion.list'

    name = fields.Char(string="List Name", required=True)
    partner_ids = fields.Many2many('res.partner', string="Partners", required=True)
