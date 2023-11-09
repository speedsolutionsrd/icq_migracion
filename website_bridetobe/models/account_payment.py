from odoo import models, fields,api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    credit_card_reference = fields.Char(string="Card Reference")
    reported_on_time = fields.Boolean(string="Reported on Time")
    cierre_caja = fields.Boolean(string="Reported")
    reported_date = fields.Date(string="Date of closed")

    # @api.onchange('payment_type')
    # def _onchange_payment_type(self):
    #     res = super(AccountPayment, self)._onchange_payment_type()
    #     journal_ids = self.env["account.journal"].search([]).filtered(lambda x: not x.restricted)
    #     res.get("domain").get("journal_id").append(("id","in",journal_ids.ids))
    #     return res

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    credit_card_reference = fields.Char(string="Card Reference")
    reported_on_time = fields.Boolean(string="Reported on Time")
    cierre_caja = fields.Boolean(string="Reported")
    reported_date = fields.Date(string="Date of closed")

    # @api.onchange('payment_type')
    # def _onchange_payment_type(self):
    #     res = super(AccountPaymentRegister, self)._onchange_payment_type()
    #     journal_ids = self.env["account.journal"].search([]).filtered(lambda x: not x.restricted)
    #     res.get("domain").get("journal_id").append(("id","in",journal_ids.ids))
    #     return res
    
    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)

        payment_vals['credit_card_reference']=self.credit_card_reference
        payment_vals['reported_on_time']=self.reported_on_time
        payment_vals['cierre_caja']=self.cierre_caja
        payment_vals['reported_date']=self.reported_date

        return payment_vals
# @api.model
    # def create(self,vals):
    #     super(AccountPayment, self).create(vals)
    #     print(self.journal_id)
