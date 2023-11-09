from datetime import timedelta

from odoo import models, api, _, fields
from odoo.exceptions import UserError


class ReportCierreCaja(models.TransientModel):
    _name = 'report.bridetobe.cierre_caja'

    date = fields.Date(string="Dia", required=True)

    def get_payment(self, payment_id):
        payment_type = ""
        transfer_type = ""
        invoice = payment_id.communication if payment_id.invoice_ids else ''
        if 'TCR' in payment_id.journal_id.code:
            payment_type = 'tarjeta'
            invoice = '%s (%s)' % (invoice or '', payment_id.credit_card_reference or '')
        elif 'TB' in payment_id.journal_id.code:
            payment_type = 'transferencia'
            transfer_type = payment_id.journal_id.code
        elif 'CSH' in payment_id.journal_id.code:
            payment_type = 'efectivo'
        elif 'CHE' in payment_id.journal_id.code:
            payment_type = 'cheque'
        else:
            payment_type = 'otros'

        return {
            'date': payment_id.payment_date,
            'partner': payment_id.partner_id.name,
            payment_type: payment_id.amount,
            'transfer_type': transfer_type,
            'invoice': invoice,
            'payment_date': fields.Datetime.from_string(payment_id.create_date) + timedelta(hours=-4)
        }

    def get_payments(self):
        payments = []
        previous_day = (fields.Datetime.from_string(self.date) - timedelta(days=3)).date()
        payment_ids = self.env['account.payment'].search([('payment_date', '<=', self.date),
                                                          ('payment_date', '>=', previous_day),
                                                          ('payment_type', '=', 'inbound'),
                                                          ('state', '!=', 'draft'),
                                                          '|', ('reported_date', '=', False),
                                                          ('reported_date', '=', self.date)])

        for payment_id in payment_ids.filtered(lambda x: self.date >= x.payment_date >= str(previous_day)):
            if payment_id.payment_date == fields.Date.today():
                payment_id.reported_on_time = True
            if not payment_id.reported_date and not payment_id.cierre_caja:
                payment_id.reported_date = self.date
                payment_id.cierre_caja = True
            payments.append(self.get_payment(payment_id))
        # for payment_id in payment_ids.filtered(
        #         lambda x: x.payment_date == self.date and not x.reported_on_time):
        #     payments.append(self.get_payment(payment_id))

        return payments

    def _print_report(self, data):
        raise UserError(_('Not implemented.'))

    @api.model
    def check_report(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'website_bridetobe.cierre_caja',
        }
        # for payment_id in self.get_payments():
        #     print payment_id.get('efectivo', 'Otro')
        #     # print payment_id.payment_date
        #     # print payment_id.partner_id.name
        #     # print payment_id.amount
        #     # if 'TCR' in payment_id.journal_id.code:
        #     #     print 'Tarjeta'
        #     # elif 'TB' in payment_id.journal_id.code:
        #     #     print 'Transaccion'
        #     # elif 'CSH' in payment_id.journal_id.code:
        #     #     print 'Efectivo'
        #     # print payment_id.journal_id.name
        #     # print payment_id.communication
        #     print "===================================="
