from odoo import models, fields, api, tools
import base64


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        mail_composer = super(MailComposer, self).send_mail(auto_commit)

        if self.model == 'account.invoice':
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            invoice_id = self.env['account.invoice'].sudo().browse(self.res_id)
            invoice_encode_id = base64.b64encode(str(self.res_id))
            invoice_url = u"%s/invoice/html/%s" % (base_url, invoice_encode_id)
            message_body = tools.html2plaintext(self.body) + "\n\n" + invoice_url

            parameters = [invoice_id.partner_id.parent_id.name or invoice_id.partner_id.name,
                          invoice_id.number,
                          "%s %s" % (invoice_id.amount_total, invoice_id.currency_id.name),
                          "%s %s" % (invoice_id.currency_id.symbol, (invoice_id.amount_total - invoice_id.residual)),
                          "%s %s" % (invoice_id.currency_id.symbol, invoice_id.residual),
                          invoice_url]

            parameters_credit = [invoice_id.partner_id.parent_id.name or invoice_id.partner_id.name,
                                 invoice_id.number,
                                 invoice_id.origin,
                                 "%s %s" % (invoice_id.amount_total, invoice_id.currency_id.name),
                                 "%s %s" % (invoice_id.residual, invoice_id.currency_id.name),
                                 invoice_url]
            if invoice_id.company_id.whatsapp_invoice_template_id or invoice_id.company_id.whatsapp_credit_template_id:
                if invoice_id.state != 'draft':
                    if invoice_id.type == 'out_invoice':
                        invoice_id.company_id.whatsapp_invoice_template_id.send_template(invoice_id.partner_id.mobile,
                                                                                         body_components=parameters)
                    elif invoice_id.type == 'out_refund':
                        invoice_id.company_id.whatsapp_credit_template_id.send_template(invoice_id.partner_id.mobile,
                                                                                        body_components=parameters_credit)

                    # self.env['whatsapp.send.message'].action_send(payload={"phone": partner_id.mobile,
                    #                                                        "body": message_body.replace('*', ''),
                    #                                                        "partner_id": partner_id.id})
        return mail_composer
