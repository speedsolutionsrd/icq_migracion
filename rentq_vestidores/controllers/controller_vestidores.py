# -*- coding: utf-8 -*-
import json
from datetime import date, datetime, timedelta

from odoo import http, _, fields
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import requests


class webVestidores(http.Controller):

    @http.route(['/dressing_room'], type='http', auth='user', website=True)
    def dressing_room_test(self):
        return request.render('rentq_vestidores.vestidores')

    @http.route(['/dressing_room_assignation'], type='http', auth="user", csrf=False)
    def get_dressing_room_assignation(self, **post):
        rentq_colas_vestidores = request.env['rentq.colas.vestidores']
        if post.get('cola_vestidor_id'):
            rentq_colas_vestidores = request.env['rentq.colas.vestidores'].browse(int(post.get('cola_vestidor_id')))
        if rentq_colas_vestidores.state_ticket == 'execute':
            return 'El Ticket %s ya esta asignado al vestidor %s' % (
                rentq_colas_vestidores.name, rentq_colas_vestidores.vestidor_id.vestidores_ids.name)
        else:
            item_cola = request.env['items.colas'].create({
                'vestidores_ids': post.get('vestidor_id'),
                'colas_vestidores_ids': post.get('cola_vestidor_id'),
            })
            if rentq_colas_vestidores:
                rentq_colas_vestidores.write({'encolado': False, 'state_ticket': 'execute'})
            update_occupation = request.env['rentq.vestidores'].browse(
                int(post.get('vestidor_id'))).write({'occupation': True, 'action_time': date.today()})

    def set_queue(self):
        user_tz = pytz.timezone(request.env.user.tz or 'UTC')
        dt = pytz.timezone('UTC').localize(datetime.now()).astimezone(user_tz)

        colas_vestidores = request.env['rentq.colas.vestidores'].sudo().search(
            [('date_start', '>=', str(dt.date()) + " 00:00:00"),
             ('date_start', '<=', str(datetime.today())),
             ('state_ticket', 'in', ['draft', 'wait', 'execute'])
             ])
        colas_vestidores_conf = []
        colas_vestidores_test = []
        notify = False
        for aux in colas_vestidores:
            if aux.type_queue == 'making':
                colas_vestidores_conf.append(aux)
            elif aux.type_queue == 'test':
                colas_vestidores_test.append(aux)
                if not aux.notified:
                    aux.notified = True
                    notify = True
        vestidores = request.env['rentq.vestidores'].sudo().search([
            ('status', '=', 'enabled')
        ])
        items_colas = request.env['items.colas'].sudo().search([])
        render_values = {
            'colas_vestidores_conf': colas_vestidores,
            'colas_vestidores_test': colas_vestidores,
            'vestidores': vestidores,
            'items_colas': items_colas,
            'notify': notify
        }

        return render_values

    @http.route(['/queue_making'], type='http', auth="user", website=True)
    def get_queue_making(self):
        values = self.set_queue()
        return request.render('rentq_vestidores.page_queue_making', values)

    @http.route(['/queue_test'], type='http', auth="user", website=True)
    def get_queue_test(self):
        values = self.set_queue()
        return request.render('rentq_vestidores.page_queue_test', values)

    @http.route(['/queue_test_anfitrion'], type='http', auth="user", website=True)
    def get_queue_test_anfitrion(self):
        values = self.set_queue()
        return request.render('rentq_vestidores.page_queue_test_anfitrion', values)

    def validate_customer(self, customer, post):
        res_partner = None
        error = dict()
        error_message = []
        sale_rentals = []
        if 'submitted' in post:
            if post.get('customer'):
                res_partner = request.env['res.partner'].sudo().search([
                    '|', '|', '|', '|',
                    ('vat', '=', customer),
                    ('customer_code', '=', customer),
                    ('name', 'ilike', customer),
                    ('mobile', 'like', customer),
                    ('phone', '=', customer)
                ])
                order_partners = request.env['sale.order'].sudo().search(
                    [('name', 'like', customer)])
                res_partner += order_partners.mapped('partner_id')
                # internal_state_entregado
                # out
                user_tz = pytz.timezone(request.env.user.tz or 'America/Santo_Domingo')
                dt = pytz.timezone('America/Santo_Domingo').localize(datetime.now()).astimezone(user_tz)
                sale_rentals = request.env['sale.rental'].sudo().search([
                    '&',
                    '&',
                    ('test_date', '>=', str(dt.date() - timedelta(days=dt.date().weekday())) + " 00:00:00"),
                    ('test_date', '<=', str(date.today()) + " 23:59:59"),
                    '|',
                    ('partner_id', 'in', res_partner.ids),
                    ('rental_product_id.default_code', 'like', customer),
                    ('state', 'not in', ['out', 'cancel']),
                    ('state_internal', '!=', request.env.ref('website_bridetobe.internal_state_entregado').id)
                ])
                sale_rentals_queued = sale_rentals.filtered(lambda x:not x.is_queued)
                if not sale_rentals:
                    error['customer'] = 'error'
                    error_message.append(
                        _('No presenta prueba para la hora y fecha actual porfavor dirijase al personal de servicio'))
                elif not sale_rentals_queued and sale_rentals:
                    error['customer'] = 'error'
                    error_message.append(_('Ya esta en cola'))
            else:
                error['customer'] = 'missing'
                error_message.append(_('Debe Ingresar su Número de Identificación o codigo de vestido'))
        if error_message:
            error['error_message'] = error_message
        render_values = {
            'error': error,
            'sale_rentals': sale_rentals_queued,
            'res_partner': res_partner,
            'view_id': post.get('view_id'),
        }

        return render_values

    @http.route(['/quotes'], type='http', auth="user", methods=['GET'], website=True)
    def quotes(self, **get):
        view_id = request.httprequest.full_path.replace('/', '').replace('?', '')
        return request.render('rentq_vestidores.page_quotes_form', {'error': dict(), 'view_id': view_id})

    @http.route(['/quotes'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def get_customer(self, **post):
        render_values = self.validate_customer(post.get('customer'), post)
        if render_values['error']:
            return request.render('rentq_vestidores.page_quotes_form', render_values)
        else:
            return request.render('rentq_vestidores.page_quotes', render_values)

    @http.route(['/take_turn_in_queue'], type='http', auth="user", website=True)
    def take_turn_in_queue(self, **post):

        colas_vestidores = request.env['rentq.colas.vestidores'].create({
            'sale_rental_id': post.get('sale_rental_id'),
            'cliente_id': post.get('cliente_id'),
            'producto_ids': [(4, [int(post.get('producto_ids'))])],
            'date_start': datetime.today(),
        })
        # sale_rental = request.env['sale.rental'].browse(int(post.get('sale_rental_id'))).write(
        #     {'is_queued': True}
        # )
        company_id = request.env.user.company_id
        post.update({'ticket': colas_vestidores.name,
                     'vestidor_printer_url': company_id.vestidor_printer_url,
                     'logo': company_id.logo_web,
                     'company': company_id.name})

        return json.dumps(post)

    @http.route(['/modista'], type='http', auth="user", website=True)
    def get_modista(self):
        user_tz = pytz.timezone(request.env.user.tz or 'America/Santo_Domingo')
        dt = pytz.timezone('America/Santo_Domingo').localize(datetime.now()).astimezone(user_tz)
        items_colas = request.env['rentq.colas.vestidores'].sudo().search([('state_ticket', '!=', 'closed'),
                                                                    ('date_start', '>=', str(dt.date()) + " 00:00:00"),
                                                                    ('date_start', '<=', str(datetime.today()))])
        return request.render('rentq_vestidores.page_modistas', {'items_colas': items_colas})

    @http.route(['/views_tv'], type='http', auth="user", website=True)
    def index_dressing_room(self, **kw):
        user_tz = pytz.timezone(request.env.user.tz or 'America/Santo_Domingo')
        dt = pytz.timezone('America/Santo_Domingo').localize(datetime.now()).astimezone(user_tz)
        items_colas = request.env['rentq.colas.vestidores'].sudo().search([('state_ticket', 'not in', ['closed', 'wait']),
                                                                    ('date_start', '>=', str(dt.date()) + " 00:00:00"),
                                                                    ('date_start', '<=', str(datetime.today()))])
        return request.render('rentq_vestidores.page_queue_tv', {
            'items_colas': items_colas
        })

    def validate_partner(self, partner_vat, post):
        error = dict()
        error_message = []
        product_ids = []
        partner_ids = []
        if 'submitted' in post:
            if post.get('partner_vat'):
                partner_ids = request.env['res.partner'].sudo().search([
                    '|',
                    '|',
                    ('vat', '=', partner_vat),
                    ('customer_code', '=', partner_vat),
                    ('name', 'ilike', partner_vat)
                ])
                product_ids = request.env['product.template'].sudo().search([('rental_code', '!=', '')])
                if not partner_ids:
                    error['partner_vat'] = 'error'
                    error_message.append(_('Cliente no Existe'))
            else:
                error['partner_vat'] = 'missing'
                error_message.append(_('Debe ingresar identificación del Cliente'))

        if error_message:
            error['error_message'] = error_message
        render_values = {
            'error': error,
            'partner_ids': partner_ids,
            'product_ids': product_ids,
            'partner_vat': post.get('partner_vat'),
            'customer_code': post.get('partner_vat'),
            'view_id': post.get('view_id'),
        }
        return render_values

    @http.route(['/assignment_to_test'], type='http', auth="user", methods=['GET'], website=True)
    def assignment_to_test(self, **get):
        view_id = request.httprequest.full_path.replace('/', '').replace('?', '')
        return request.render('rentq_vestidores.page_queue_test_set_partner_form',
                              {'error': dict(), 'view_id': view_id})

    @http.route(['/assignment_to_test'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def get_partner(self, **post):
        render_values = self.validate_partner(post.get('partner_vat'), post)
        if render_values['error']:
            return request.render('rentq_vestidores.page_queue_test_set_partner_form', render_values)
        else:
            return request.render('rentq_vestidores.page_queue_test_set_partner', render_values)

    @http.route(['/test_queue_assignation'], type='http', auth="user", website=True)
    def get_test_queue_assignation(self, **post):
        colas_vestidores = request.env['rentq.colas.vestidores'].create({
            'cliente_id': post.get('cliente_id'),
            'producto_ids': [(6, 0, [int(x) for x in request.httprequest.form.getlist('products[]')])],
            'type_queue': 'test',
            'date_start': datetime.today(),
        })
        return request.redirect(post.get('redirect_to'))

    @http.route(['/register_customer'], type='http', auth='user', website=True, methods=['GET'])
    def render_register_customer(self, **get):
        error = dict()
        error_message = []
        partner_ids = []
        qweb_template = 'rentq_vestidores.id_partner_data'
        product_ids = request.env['product.template'].sudo().search([('rental_code', '!=', '')])

        return request.render(qweb_template, {
            'error': error,
            'partner_temp': get,
            'country_ids': request.env['res.country'].sudo().search([]),
            'form_method': 'post',
            'seller': request.env['hr.employee'],
            'view_id': get.get('view_id'),
            'partner_ids': request.env['res.partner'],
            'countries': request.env['res.country'].sudo().search([]),
            'partner': request.env['res.partner'],
            'product_ids': product_ids
        })

    @http.route(['/save_customer'], type='http', auth="user", website=True)
    def get_customer_new(self, **post):
        customers = request.env['res.partner'].create({
            'name': post.get('name'),
            'customer_code': post.get('customer_code'),
            'mobile': post.get('mobile'),
            'phone': post.get('phone'),
            'vat': post.get('vat'),
            'email': post.get('email'),
            'street': post.get('street'),
            'city': post.get('city'),
            'country_id': int(post.get('country_id'))
        })
        res_partners = request.env['res.partner'].sudo().search([])
        for res_partner in res_partners:
            if res_partner.vat == post.get('vat') and res_partner.customer_code == post.get('customer_code'):
                colas_vestidores = request.env['rentq.colas.vestidores'].create({
                    'cliente_id': res_partner.id,
                    'producto_ids': [(6, 0, [int(x) for x in request.httprequest.form.getlist('products[]')])],
                    'type_queue': 'test',
                    'date_start': date.today(),
                })
        return request.redirect('/queue_test')

    @http.route(['/end_process_dressing_room'], type='http', auth="user", website=True)
    def get_end_process_dressing_room(self, **post):
        if not post.get('stop_counter'):
            if post.get('cola_vetidor_id'):
                cola = request.env['rentq.colas.vestidores'].browse(
                    int(post.get('cola_vetidor_id')))
                cola.write({'state_ticket': 'closed',
                            'date_start': datetime.today()})
                # cola.sale_rental_id.is_queued = False
        else:
            request.env['rentq.colas.vestidores'].browse(
                int(post.get('cola_vetidor_id'))).write({'state_ticket': 'wait', 'date_start': datetime.today()})
        if post.get('vestidor_id'):
            request.env['rentq.vestidores'].browse(
                int(post.get('vestidor_id'))).write({'occupation': False, 'action_time': datetime.today()})

        if post.get('cola_vetidor_id'):
            request.env['items.colas'].sudo().search(
                [('colas_vestidores_ids', '=', int(post.get('cola_vetidor_id')))]).unlink()
        else:
            request.env['items.colas'].sudo().search([('vestidores_ids', '=', int(post.get('vestidor_id')))]).unlink()

        return request.redirect(post.get('redirect_to'))

    @http.route(['/remove_customer'], type='http', auth="user", website=True)
    def remove_customer(self, **post):
        ticket_id = request.env['rentq.colas.vestidores'].browse(int(post.get('cola_vetidor_id')))
        ticket_id.state_ticket = 'closed'

        return request.redirect(post.get('redirect_to'))
