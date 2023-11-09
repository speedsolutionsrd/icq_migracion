from odoo import models, fields


class WhatsappAccountValidation(models.TransientModel):
    _name = "whatsapp.account.validation"

    qr_image = fields.Binary(string="QR Code")
    message = fields.Char(string="Message")
