from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    whatsapp_invoice_template_id = fields.Many2one('meta.connect.whatsapp.template', string="Invoice Template")
    whatsapp_credit_template_id = fields.Many2one('meta.connect.whatsapp.template', string="Credit Note Template")
    # whatsapp_receipt_no_test_template_id = fields.Many2one('meta.connect.whatsapp.template', string="Receipt no Test Template")

    def check_template(self, template_id, parameter_count):
        if template_id and template_id.parameter_count != parameter_count:
            raise ValidationError("Template invalido debe tener %s parametros" % parameter_count)

    @api.constrains('whatsapp_invoice_template_id')
    def check_whatsapp_invoice_template_id(self):
        self.check_template(self.whatsapp_invoice_template_id, 6)

    @api.constrains('whatsapp_credit_template_id')
    def check_whatsapp_credit_template_id(self):
        self.check_template(self.whatsapp_credit_template_id, 6)

    #
    # @api.constrains('whatsapp_receipt_no_test_template_id')
    # def check_whatsapp_receipt_no_test_id(self):
    #     self.check_template(self.whatsapp_receipt_no_test_template_id, 1)
    #     # if self.whatsapp_receipt_no_test_id and self.whatsapp_receipt_no_test_id.parameter_count != 1:
    #     #     raise ValidationError("Template invalido debe tener 1 parametro")


class VestidoresConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    whatsapp_invoice_template_id = fields.Many2one(related='company_id.whatsapp_invoice_template_id')
    whatsapp_credit_template_id = fields.Many2one(related='company_id.whatsapp_credit_template_id')
    # whatsapp_receipt_no_test_template_id = fields.Many2one(related='company_id.whatsapp_receipt_no_test_template_id')
