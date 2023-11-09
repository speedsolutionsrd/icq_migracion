import json

import requests

from odoo import models
from odoo.exceptions import ValidationError


class WhatsappMessage(models.Model):
    _inherit = 'whatsapp.send.message'

    def call_chat_api(self, url, payload, request_type=requests.get):
        base_url, headers, params = self.get_data()
        if not base_url:
            raise ValidationError("No Configuration detected from Whatsapp Connect")
        try:
            response = request_type("%s%s" % (base_url, url), data=json.dumps(payload), headers=headers,
                                    params=params, verify=False).json()
            return response
        except:
            return {'error': 'Whatsapp Connection Error'}

    def get_data(self):
        ICPSudo = self.env['ir.values'].sudo()
        url = ICPSudo.get_default('res.config.settings', 'url_api')
        headers = {'content-type': 'application/json'}
        params = {"token": ICPSudo.get_default('res.config.settings', 'auth_token')}
        return url, headers, params

    def action_send(self, context=False, url="/message", payload=False, request_type=requests.post):
        phone = self.mobile or payload.get('phone', False) or payload.get('mobile', False)
        if phone:
            if phone.startswith('+1'):
                phone = phone.replace('+', '')
            elif not phone.startswith('1'):
                phone = '1%s' % phone
        payload = payload or {"phone": phone, "body": self.message}
        if 'phone' in payload:
            payload['phone'] = phone
        response = self.call_chat_api(url, payload, request_type)
        state = 'send'
        if 'error' in response:
            if self:
                self.state = 'fail'
            # raise ValidationError(response['error'])
        if self:
            self.state = state
        else:
            whatsapp_message = self.create({'mobile': payload.get('phone'),
                                            'message': payload.get('body'),
                                            'partner_id': payload.get('partner_id'),
                                            'state': state})
