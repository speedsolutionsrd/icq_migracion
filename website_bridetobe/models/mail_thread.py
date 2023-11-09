from odoo import models, api


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _get_message_unread(self):
        super(MailThread, self)._get_message_unread()
        for record in self:
            for message_id in record.message_ids:
                if message_id.author_id.name == message_id.create_uid.name:
                    if record.message_unread_counter > 0:
                        record.message_unread_counter -= 1

# Este metodo ya existe en odoo 16 con otro nombre, buscar en el modelo mail.channel.member metodo _compute_message_unread