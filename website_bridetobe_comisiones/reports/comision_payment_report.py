# from odoo import models, api
#
#
# class ComisionPaymentReport(models.AbstractModel):
#     _name = 'report.website_bridetobe_comisiones.payment_report'
#
#
#     @api.model
#     def render_html(self, docids, data=None):
#         report_obj = self.env['report']
#         docs = []
#         report = report_obj._get_report_from_name('website_bridetobe_comisiones.payment_report')
#         comision_payment_ids = self.env['bridetobe.comision.payment'].browse(docids)
#
#         for comision_payment in comision_payment_ids:
#             employee_ids = self.env['hr.employee'].search([('department_id','=',comision_payment.tarifa_comision_id.name.id)])
#             payment_data = []
#             for employee_id in employee_ids:
#                 comision_ids = comision_payment.comision_ids.search([('comision_payment_id','=',comision_payment.id),
#                                                                      ('employee_id','=',employee_id.id)])
#                 if comision_ids:
#                     payment_data.append({'employee_id':employee_id,
#                                          'comision_ids':comision_ids})
#
#             docs.append({'start_date':comision_payment.start_date,
#                          'end_date':comision_payment.end_date,
#                          'payment_data': payment_data})
#
#
#         docargs = {
#             'doc_ids': docids,
#             'doc_model': report.model,
#             'docs': docs,
#             # 'docs': self.env['bridetobe.comision.payment'].browse(docids),
#         }
#         return report_obj.render('website_bridetobe_comisiones.payment_report', docargs)
