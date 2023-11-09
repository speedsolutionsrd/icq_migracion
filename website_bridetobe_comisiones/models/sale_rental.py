from odoo import models, fields


class SaleRental(models.Model):
    _inherit = 'sale.rental'

    comision_ids = fields.One2many('bridetobe.comision', 'rental_id', string="Comision")

    def create_comisiones(self, payment_id, employee_id):
        comision_ids = []
        for sale_rental in self:
            tarifa_comision = self.env['bridetobe.tarifa.comision'].search(
                [("name", "=", employee_id.department_id.id),
                 ("category_id", "in", [sale_rental.rented_product_id.categ_id.id, False])])
            invoice_state = 1
            invoice_balance = 1
            change = sale_rental.has_product_change
            invoice_ids = sale_rental.start_order_id.mapped('invoice_ids')

            for invoice_id in invoice_ids:
                if invoice_id.state in ['draft', 'cancel']:
                    invoice_state = 0
                if invoice_id.residual > 0 or invoice_id.state in ['draft', 'cancel']:
                    invoice_balance = 0

            tarifa_id = tarifa_comision.comision_line.filtered(lambda x: x.invoice_state == invoice_state and
                                                                         x.invoice_balance == invoice_balance and
                                                                         x.change == change and
                                                                         x.internal_state == sale_rental.state_internal)
            if tarifa_id:
                comision_ids.append({"name": sale_rental.rented_product_id.id,
                                     'rental_id': sale_rental.id,
                                     'employee_id': employee_id.id,
                                     'state_internal': sale_rental.state_internal.id,
                                     'amount': tarifa_id.amount,
                                     'comision_payment_id': payment_id})
            elif tarifa_comision:
                comision_ids.append({"name": sale_rental.rented_product_id.id,
                                     'rental_id': sale_rental.id,
                                     'employee_id': employee_id.id,
                                     'state_internal': sale_rental.state_internal.id,
                                     'amount': tarifa_comision.amount,
                                     'comision_payment_id': payment_id})
            else:
                comision_ids.append({"name": sale_rental.rented_product_id.id,
                                     'rental_id': sale_rental.id,
                                     'employee_id': employee_id.id,
                                     'state_internal': sale_rental.state_internal.id,
                                     'amount': 0.0,
                                     'comision_payment_id': payment_id})
        for comision in comision_ids:
            self.env['bridetobe.comision'].sudo().create(comision)
