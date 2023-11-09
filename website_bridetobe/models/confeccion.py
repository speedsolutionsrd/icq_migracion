from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Confeccion(models.Model):
    _name = 'bridetobe.confeccion'
    _description = 'Manejador de Confecciones BrideToBe'
    _inherit = ['mail.thread']
    _order = "id DESC"

    name = fields.Char(string='Referencia', required=True,
                       copy=False, readonly=True,
                       index=True, default=lambda self: 'New')
    partner_id = fields.Many2one('res.partner', string="Cliente")
    tipo_confeccion = fields.Selection([('renta', 'Renta Exclusiva'),
                                        ('cliente', 'Cliente')],
                                       string="Tipo Confeccion", default="cliente")
    modista_id = fields.Many2one('hr.employee', string='Modista')
    tela = fields.Text(string="Materiales y Tipo de tela solicitada")
    materiales = fields.Text(string="Materiales y Tela recibida")
    c_moda = fields.Char(string="Suministro Moda")
    suministro_materiales = fields.Selection([('p_cliente', 'Pendiente de Recibir del Cliente'),
                                              ('e_cliente', 'Entregada por Cliente'),
                                              ('c_tienda', 'Pendiente de Comprar Por Tienda')],
                                             string="Suministro Materiales")
    event_date = fields.Date(string="Fecha del Evento")
    event_place = fields.Char(string="Lugar del Evento")
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    costo = fields.Float(string="Precio Final")
    description = fields.Text(string="Descripcion")
    notes = fields.Text(string="Observaciones")
    color = fields.Char(string="Color")
    display_name = fields.Char(string="Cliente", compute="_compute_display_name")

    invoice_created = fields.Boolean(string="Facturado", default=False)
    medidas_pruebas = fields.One2many('bridetobe.medida_prueba', 'confeccion_id', string='Medidas y Pruebas')
    metric_ids = fields.One2many("confection.metric", "confection_id", string="Medidas", required=True)
    next_test = fields.Datetime('Proxima Prueba', compute="_compute_next_test", search="_search_next_test")
    delivery_date = fields.Datetime(string='Fecha de Entrega')

    @api.model
    def _get_default_internal_state(self):
        return self.state_internal.search([('sequence', '=', 1)])

    state_internal = fields.Many2one('sale.rental.internal.state',
                                     string="Estado Interno", ondelete="restrict",
                                     default=_get_default_internal_state)

    def get_details(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bridetobe.confeccion',
            'res_id': self.id,
            'context': self.env.context,
            'view_id': self.env.ref('website_bridetobe.view_bridetobe_confeccion_form').id,
        }

    def get_next_test(self):
        if self.medidas_pruebas:
            medida_id = self.medidas_pruebas.search([('state', '=', 'pending'),
                                                     ('confeccion_id', '=', self.id)], order='date_time asc', limit=1)
            return medida_id.date_time
        return False

    @api.model
    def _compute_next_test(self):
        for order in self:
            order.next_test = order.get_next_test()

    @api.model
    def _search_next_test(self, operator, value):
        if operator == '=':
            operator = '=='
        condition = "x.next_test %s '%s'" % (operator, value)
        confection_ids = self.search([]).filtered(lambda x: eval(condition))
        return [('id', 'in', confection_ids.ids)]

    @api.model
    def _compute_display_name(self):
        for order in self:
            if order.color:
                order.display_name = '%s (%s)' % (order.partner_id.name, order.color)
            else:
                order.display_name = order.partner_id.name

    @api.model
    def write(self, vals):
        metric_ids = []
        if 'metrics' in vals:
            for metric in vals.get('metrics', {}):
                value = vals.get('metrics')[metric]
                id = metric.split('_')[1]
                metric_ids.append((0, 0, {'metric_id': id, 'amount': value}))
            del vals['metrics']
            vals.update({'metric_ids': metric_ids})
        return super(Confeccion, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('modista_id') == '0' or vals.get('modista_id') == 0:
            del vals['modista_id']

        metric_ids = []
        for metric in vals.get('metrics'):
            value = vals.get('metrics')[metric]
            id = metric.split('_')[1]
            metric_ids.append((0, 0, {'metric_id': id, 'amount': value}))
        vals.update({'metric_ids': metric_ids})

        vals['name'] = self.env['ir.sequence'].next_by_code('bridetobe.confeccion')

        result = super(Confeccion, self).create(vals)
        return result

    @api.model
    def create_invoice(self):
        if not self.invoice_created:
            product_template = self.env.ref('website_bridetobe.confecciones_product')
            product_id = self.env['product.product'].search([('product_tmpl_id','=',product_template.id)], limit=1)
            invoice_obj = self.env['account.invoice']

            self.invoice_created = True
            self.invoice_id = invoice_obj.create({'partner_id': self.partner_id.id,
                                                  'event_date': self.event_date,
                                                  'type': 'out_invoice',
                                                  'name': self.name,
                                                  'amount_total': self.costo,
                                                  })

            self.invoice_id.invoice_line_ids.create({'name': self.description,
                                                     'product_id': product_id.id,
                                                     'quantity': 1,
                                                     'invoice_line_tax_ids': [(6,0,product_template.taxes_id.ids)],
                                                     'account_id': self.invoice_id.journal_id.default_credit_account_id.id,
                                                     'price_unit': self.costo,
                                                     'invoice_id': self.invoice_id.id})
            self.invoice_id.compute_taxes()

    @api.model
    def action_view_invoice(self):
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        action['res_id'] = self.invoice_id.id
        return action

    def action_show_dates(self):
        self.ensure_one()
        view = self.env.ref('website_bridetobe.confeccion_medida_prueba_form')
        return {
            'name': 'Medidas y Pruebas',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bridetobe.confeccion',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(self.env.context),
        }

    def post_message(self, message_body=False, parameters=False):
        if message_body:
            return message_body
        return False


class ConfectionMetric(models.Model):
    _name = 'confection.metric'
    _rec_name = "metric_id"

    metric_id = fields.Many2one('bridetobe.metric', string="Descripcion", required=True)
    confection_id = fields.Many2one('bridetobe.confeccion')
    amount = fields.Float(string="Medida", required=True)

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount <= 0:
            raise ValidationError("Las Medidas deben ser mayor que 0.0")

    _sql_constraints = [
        ('metric_uniq', 'unique(metric_id,confection_id)', 'Medida ya existe'),
    ]


class MedidasPruebas(models.Model):
    _name = 'bridetobe.medida_prueba'
    _description = 'Historico Pruebas Confeccion'

    date_time = fields.Datetime(string='Fecha y hora de Prueba', required=True)
    observaciones = fields.Text(string="Observaciones")
    confeccion_id = fields.Many2one('bridetobe.confeccion',
                                    string="Confeccion")
    state = fields.Selection([('pending', 'Pendiente'),
                              ('canceled', 'Cancelada'),
                              ('rejected', 'No Asistio'),
                              ('maked', 'Realizada')], string="Status", default="pending")

    def post_message(self, message_body=False, parameters=False):
        if message_body:
            self.confeccion_id.message_ids.create({
                "subject": "Detalles de su Confeccion" + self.confeccion_id.name,
                "subtype_id": 1,
                "res_id": self.confeccion_id.id,
                "partner_ids": [(4, self.confeccion_id.partner_id.id)],
                "needaction_partner_ids": [(4, self.confeccion_id.partner_id.id)],
                "body": message_body,
                "record_name": self.confeccion_id.display_name,
                "date": datetime.today(),
                "model": 'bridetobe.confeccion',
                "author_id": self.env.user.id,
                "message_type": "email",
                "email_from": self.env.user.email})
            return message_body
        return False

    @api.model
    def create(self, vals):
        medida_prueba = super(MedidasPruebas, self).create(vals)
        state_internal = medida_prueba.confeccion_id.state_internal
        if state_internal.sequence == 1:
            medida_prueba.confeccion_id.state_internal = state_internal.next_state()
        self_test_date = fields.Datetime.from_string(medida_prueba.date_time) + timedelta(hours=-4)
        test_date = datetime.strftime(self_test_date, '%d/%m/%Y %I:%M %p')
        message_body = False
        custom_message = False
        state_internal = medida_prueba.confeccion_id.state_internal

        if medida_prueba.confeccion_id.state_internal.message_body_confecciones and medida_prueba.confeccion_id.state_internal.message_send:
            message_body = state_internal.message_body_confecciones
            custom_message = state_internal
        else:
            custom_message = self.env['sale.rental.custom.message'].get_message(self, 'date_time')
            message_body = custom_message.message_body

        message_data = [medida_prueba.confeccion_id.partner_id.name,
                        ".",
                        medida_prueba.confeccion_id.state_internal.name,
                        medida_prueba.confeccion_id.modista_id.name,
                        medida_prueba.confeccion_id.name,
                        test_date,
                        medida_prueba.confeccion_id.delivery_date,
                        ".",
                        "."]
        if message_body:
            message_body = message_body.format(*message_data)
            medida_prueba.post_message(message_body, custom_message, message_data)
        return medida_prueba

    @api.model
    def write(self, vals):
        medida_prueba = super(MedidasPruebas, self).write(vals)
        self_test_date = fields.Datetime.from_string(self.date_time) + timedelta(hours=-4)
        test_date = datetime.strftime(self_test_date, '%d/%m/%Y %I:%M %p')
        for key in vals.keys():
            custom_message = self.env['sale.rental.custom.message'].get_message(self, key)
            if custom_message.message_body:
                parameters = [self.confeccion_id.partner_id.name,
                              ".",
                              self.confeccion_id.state_internal.name,
                              self.confeccion_id.modista_id.name,
                              self.confeccion_id.name,
                              test_date,
                              self.confeccion_id.delivery_date,
                              ".",
                              "."]
                message_body = custom_message.message_body.format(*parameters)
                self.post_message(message_body, custom_message, parameters)
        return medida_prueba
