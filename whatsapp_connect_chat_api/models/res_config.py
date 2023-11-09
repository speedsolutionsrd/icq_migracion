from odoo import models
from odoo.exceptions import ValidationError


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    def test_whatsapp_config(self):
        self.sudo().execute()
        response = self.env['whatsapp.send.message'].call_chat_api("/status", {})
        qr_code = response.get('qrCode', False)
        error = response.get('error', False)
        if qr_code:
            qr_code = qr_code.replace("data:image/png;base64,", "")
            message = False
        elif error:
            message = error
        else:
            message = "Account Linked"
            qr_code = False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Account Status',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'whatsapp.account.validation',
            'context': {"default_qr_image": qr_code,
                        "default_message": message},
            'view_id': self.env.ref('whatsapp_connect_chat_api.whatsapp_account_validation_form').id,
            'target': 'new',
        }

    def whatsapp_logout(self):
        self.env['whatsapp.send.message'].call_chat_api("/logout", {})
        return self.test_whatsapp_config()
