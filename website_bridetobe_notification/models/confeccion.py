from odoo import models, fields, tools
from datetime import datetime, timedelta


class MedidasPruebas(models.Model):
    _inherit = 'bridetobe.medida_prueba'

    def post_message(self, message_body, custom_message, parameters):
        super(MedidasPruebas, self).post_message(message_body)
        # if message_body:
        #     self.env['whatsapp.send.message'].action_send(payload={"phone": self.confeccion_id.partner_id.mobile,
        #                                                            "body": tools.html2plaintext(message_body).replace('*',''),
        #                                                            "partner_id": self.confeccion_id.partner_id.id})
        if custom_message._name == "sale.rental.internal.state":
            whatsapp_template_id = custom_message.whatsapp_template_confeccion_id
            whatsapp_template_body_parameter_ids = custom_message.whatsapp_template_body_parameter_confeccion_ids
        else:
            whatsapp_template_id = custom_message.whatsapp_template_id
            whatsapp_template_body_parameter_ids = custom_message.whatsapp_template_body_parameter_ids

        if whatsapp_template_id:
            body_components = []
            for parameter in whatsapp_template_body_parameter_ids:
                body_components.append(parameters[int(parameter.value)])
            whatsapp_template_id.sudo().send_template(self.confeccion_id.partner_id.mobile,
                                                      body_components=body_components)


class Confeccion(models.Model):
    _inherit = 'bridetobe.confeccion'

    def post_message(self, message_body, custom_message, parameters):
        super(Confeccion, self).post_message(message_body)
        if custom_message._name == 'sale.rental.internal.state':
            whatsapp_template_id = custom_message.whatsapp_template_confeccion_id
        else:
            whatsapp_template_id = custom_message.whatsapp_template_id
        if whatsapp_template_id:
            fecha = str(datetime.today().date())
            hora = str(datetime.today().time())
            whatsapp_template_id.sudo().send_template(parameters[0],
                                                      body_components=[parameters[1], fecha[:10], hora[:5],
                                                                       parameters[2]])
