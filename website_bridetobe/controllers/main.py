# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo.addons.web.controllers.home import Home

from odoo import http, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


# class Website(Home):
#     @http.route('/', type='http', auth="public", website=True)
#     def index(self, **kw):
#         page = 'website_bridetobe.homepage'
#         return self.page(page)


missing_message = "Algunos campos requeridos estan vacios."


class BridetoBe(http.Controller):
    update_partner_mandatory_fields = [
        ["country_id", "Debe seleccionar un Pais"],
        ["name", "Digite su nombre"],
        ["mobile", "Digite su numero de movil"],
        ["phone", "Digite su numero de Telefono"],
        ["email", "Digite su Email"],
        ["street", "Digite la Calle"],
        ["city", "Debe digitar su ciudad"]]

    mandatory_fields = ["country_id", "name", "mobile", "phone", "email", "street", "city", "seller_code", "cadera",
                        "event_place", "busto", "event_date", "cintura", "product_barcode", "vat"]

    event_data_mandatory_fields = [
        ["cadera", "Debe digitar la medida de la Cadera"],
        ["event_place", "Debe digitar el Lugar del evento"],
        ["busto", "Debe digitar la medida del Busto"],
        ["event_date", "Debe digitar la fecha del Evento"],
        ["cintura", "debe digitar la medida de la Cintura"]]

    def get_modista_ids(self):
        return request.env['hr.employee'].sudo().search_read(
            [('department_id', '=', request.env.ref('website_bridetobe.modista').id)], ['name'])

    def get_country_ids(self):
        return request.env['res.country'].sudo().get_website_sale_countries('new')

    def validate_required_fields(self, post, error=dict(), mandatory_fields=[]):
        for field in mandatory_fields:
            field = field[0]
            if field in post and not post.get(field):
                error[field] = 'missing'
        if 'missing' in error.values():
            if error.get('error_message') and missing_message not in error.get('error_message', {}):
                error['error_message'].append(_(missing_message))
            elif not error.get('error_message'):
                error['error_message'] = [_(missing_message)]
        return error

    def get_event_week(self, event_date):
        # date = datetime.strptime(event_date, DEFAULT_SERVER_DATE_FORMAT)
        # date_start = date - timedelta(days=date.weekday())
        # date_end = date_start + timedelta(days=8)
        #
        # return datetime.strftime(date_start, DEFAULT_SERVER_DATE_FORMAT), \
        #        datetime.strftime(date_end, DEFAULT_SERVER_DATE_FORMAT)
        return request.env['sale.rental'].get_event_week(event_date)

    def put_missing_field(self, error, field):
        if field:
            error[field] = 'missing'

    def put_error_message(self, error, error_message, field=False):
        self.put_missing_field(error, field)
        if error.get('error_message'):
            error['error_message'].append(error_message)
        else:
            error['error_message'] = [error_message]

    def validate_event_date(self, post, error):
        if post.get('event_date'):
            event_date = datetime.strptime(post.get("event_date"), DEFAULT_SERVER_DATE_FORMAT).date()
            if event_date < datetime.now().date():
                self.put_error_message(error, "Fecha del Evento no puede ser anterior a fecha actual", "event_date")
            start_date, end_date = self.get_event_week(datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))
            if event_date >= datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT).date() and \
                    event_date <= datetime.strptime(end_date,
                                                    DEFAULT_SERVER_DATE_FORMAT).date():

                self.validate_required_fields(post, error, ['delivery_date', 'delivery_time'])
                if post.get('modista_id') == '0':
                    self.put_missing_field(error, 'modista_id')
                    self.put_missing_field(error, 'modista_id')
                    self.put_missing_field(error, 'delivery_date')
                    self.put_missing_field(error, 'delivery_time')
        else:
            self.validate_required_fields(post, error, ['event_date'])

    def _get_product_availability(self, product_barcode, product_ids, product_valid, post, error):
        for code in product_barcode.split(','):
            product = request.env['product.template'].sudo().search([('barcode', '=', code),
                                                                     ('rented_product_id', '!=', False)])
            if product:
                event_dates = dict(
                    filter(lambda item: 'event_date' in item[0] and item[0] != 'event_date_confirm',
                           sorted(post.items())))
                for key in event_dates:
                    event_date = post.get(key)
                    date_start, date_end = self.get_event_week(event_date)

                    product_availability = request.env['sale.rental'].sudo().search(
                        [('rental_product_id', '=', product.id),
                         ('start_date', '>=', date_start),
                         ('start_date', '<=', date_end),
                         ('state', '!=', 'cancel')])
                    if product_availability:
                        product_barcode = product_barcode.replace(product.barcode, '')
                        self.put_error_message(error, _("Articulo %s no esta disponible para la fecha %s" % (
                            code, event_date)), key)
                    elif product.barcode not in product_valid:
                        product_valid.append(product.barcode)
                        product_id = request.env['product.product'].sudo().search(
                            [('product_tmpl_id', '=', product.id),
                             ('barcode', '=', product.barcode)])
                        product_ids.insert(0, {"barcode": product.barcode,
                                               "name": product.name,
                                               "image": product.can_image_1024_be_zoomed,
                                               "price": product.list_price,
                                               "id": product_id.id})
                    # else:
                    #     product_barcode = product_barcode.replace(product.barcode + ',', '', 1)
                    #     self.put_error_message(error, _("El articulo %s ya fue agregado a la orden" % code),
                    #                            'product_barcode')
            else:
                self.put_error_message(error, _("Codigo de Articulo %s Invalido" % code), 'product_barcode')

    def validate_seller(self, post):
        error = dict()
        seller_code = post.get('seller_code')
        seller_id = request.env['hr.employee'].sudo().search([('seller_code', '=', seller_code)])
        product_ids = []
        product_valid = []
        self.validate_required_fields(post, error, self.event_data_mandatory_fields)
        if post.get('seller_code') and not seller_id:
            error['seller_code'] = 'error'
        self.validate_event_date(post, error)
        if not error:
            self._get_product_availability(post.get('product_barcode'), product_ids, product_valid, post, error)
        render_values = {'error': error, 'product_ids': product_ids, 'seller_id': seller_id.sudo()}
        post.pop('product_ids')
        render_values.update(post)
        return render_values

    def update_partner(self, error, partner_id, post):
        partner = request.env['res.partner'].sudo()
        busto, cintura, cadera = '0.0'
        if not error:
            if post.get('busto'):
                busto = post.get('busto')
            if post.get('cintura'):
                cintura = post.get('cintura')
            if post.get('cadera'):
                cadera = post.get('cadera')

            try:
                if not post.get('customer_code'):
                    post.update({'customer_code': post.get('vat')})
                if partner_id:
                    partner_id.write(post)
                else:
                    partner_id = partner.create(post)
                if not partner_id.metric_ids:
                    partner_id.write(
                        {'metric_ids': [
                            (0, 0, {'amount': float(busto),
                                    'metric_id': request.env.ref('website_bridetobe.metric_busto').id}),
                            (0, 0, {'amount': float(cintura),
                                    'metric_id': request.env.ref('website_bridetobe.metric_cintura').id}),
                            (0, 0, {'amount': float(cadera),
                                    'metric_id': request.env.ref('website_bridetobe.metric_cadera').id})]})
                else:
                    partner_id.metric_ids.filtered(
                        lambda x: x.metric_id == request.env.ref('website_bridetobe.metric_busto')).write(
                        {'amount': float(busto)})
                    partner_id.metric_ids.filtered(
                        lambda x: x.metric_id == request.env.ref('website_bridetobe.metric_cintura')).write(
                        {'amount': float(cintura)})
                    partner_id.metric_ids.filtered(
                        lambda x: x.metric_id == request.env.ref('website_bridetobe.metric_cadera')).write(
                        {'amount': float(cadera)})
            except Exception as e:
                self.put_error_message(error, e[0] or "RNC/Cedula debe ser numerico (Whatsapp si no tiene)", 'vat')
            return partner_id

    def validate_partner(self, post, error=dict()):
        partner_id = False
        partner = request.env['res.partner'].sudo()

        if 'search_partner' in post and post.get('vat', False):
            partner_id = partner.search([('vat', '=', post.get('vat'))], limit=1)
            if not partner_id:
                try:
                    partner_id = partner.create({'name': post.get('vat'),
                                                 'vat': post.get('vat')})
                    partner_id.onchange_partner_name()
                except:
                    pass
        elif 'submit' in post and post.get('partner_id'):
            partner_id = partner.browse(int(post.get('partner_id')))
            self.validate_required_fields(post, error, self.update_partner_mandatory_fields)
            self.update_partner(error, partner_id, post)
        elif 'submit' in post and not post.get('partner_id'):
            if post.get('vat'):
                partner_id = partner.search([('vat', '=', post.get('vat'))], limit=1)
            if not partner_id:
                self.validate_required_fields(post, error, self.update_partner_mandatory_fields)
                partner_id = self.update_partner(error, partner_id, post)

            else:
                self.put_error_message(error, "Cliente no Existe")

        if post.get('event_date') != post.get('event_date_confirm'):
            self.put_error_message(error, "Fecha de Evento Incorrecta Contacte a su Vendedor (a)", 'event_date_confirm')

        if not partner_id and 'search_partner' in post:
            self.put_error_message(error, "Cliente no existe", 'vat')

        render_values = {
            'modista_ids': self.get_modista_ids(),
            'country_ids': self.get_country_ids(),
            'partner_id': partner_id
        }
        if error:
            render_values.update({'error': error})
        return render_values

    def get_rent_values(self, view_id):
        return {'error': dict(), 'view_id': view_id, 'modista_ids': self.get_modista_ids(),
                'country_ids': self.get_country_ids()}

    @http.route(['/renta'], type='http', auth="public", methods=['GET'], website=True)
    def renta(self, **get):
        request.session['order_id'] = None
        view_id = request.httprequest.full_path.replace('/', '').replace('?', '')
        return request.render('website_bridetobe.set_seller', self.get_rent_values(view_id))

    @http.route(['/renta'], type='http', auth="public", methods=['POST'], website=True, csrf=True)
    def get_seller(self, **post):
        render_values = self.validate_seller(post)
        render_values.update(self.validate_partner(render_values, error=render_values.get('error')))
        if render_values.get('error'):
            return request.render('website_bridetobe.set_seller', render_values)
        else:
            error = False
            if 'submit' in post:
                error = self.validate_required_fields(post, mandatory_fields=self.mandatory_fields)
            elif 'search_partner' in post:
                return request.render('website_bridetobe.set_seller', render_values)
            if error:
                render_values.update({'error': error})
                return request.render('website_bridetobe.set_seller', render_values)
            else:
                render_values.update({'product_ids': render_values.get('product_ids')})
                order_id = self._event_data(render_values)
                render_values.update({'order_id': order_id})
                request.session['order_id'] = order_id.id
                return request.render('website_bridetobe.event_data', render_values)

    @http.route(['/renta/partner'], type='http', auth="public", methods=['POST'],
                website=True, csrf=True)
    def get_partner(self, **post):
        render_values = self.validate_partner(post)
        if not render_values.get('partner_id') or 'submit' not in post or render_values.get('error'):
            return request.render('website_bridetobe.set_partner', render_values)
        else:
            render_values.update({'product_ids': eval(render_values.get('product_ids'))})
            return request.render('website_bridetobe.event_data', render_values)

    @http.route(['/renta/event_data'], type='http', auth="public", methods=['POST'],
                website=True, csrf=True)
    def event_data(self, **post):
        # if not request.session.get('order_id'):
        #     order_id = self._event_data(post)
        #     post.update({'order_id': order_id})
        #     request.session['order_id'] = order_id.id
        # else:
        #     order_id = request.session.get('order_id')
        #     post.update({'order_id': request.env['sale.order'].sudo().browse(order_id)})
        # return request.render('website_bridetobe.order_confirmation', post)
        order_id = request.session.get('order_id')
        post.update({'order_id': request.env['sale.order'].sudo().browse(order_id)})
        return self.order_confirmation(**post)

    def _event_data(self, post):
        extra_weeks = dict(
            filter(lambda item: 'event_date' in item[0] and item[0] != 'event_date_confirm', post.items()))
        partner_id = request.env['res.partner'].sudo().browse(int(post.get("partner_id")))
        seller_id = request.env['hr.employee'].sudo().browse(int(post.get("seller_id")))
        product_ids = post.get('product_ids')
        extra_weeks_date = post.get('event_date')
        if len(extra_weeks) > 1:
            extra_weeks_date = post.get('event_date_' + str(len(extra_weeks) - 1))
        if post.get('exchange') == 'true':
            exchange = True
        elif not post.get('exchange'):
            exchange = False
        else:
            exchange = False
        data = {
            "partner_id": partner_id.id,
            "event_date": post.get('event_date'),
            "event_place": post.get('event_place'),
            "busto": post.get('busto'),
            "cintura": post.get('cintura'),
            "cadera": post.get('cadera'),
            "default_start_date": datetime.strptime(post.get('event_date'),
                                                    DEFAULT_SERVER_DATE_FORMAT) - relativedelta(days=7),
            "default_end_date": extra_weeks_date,
            "comments": post.get('comments'),
            "seller_id": seller_id.id,
            "exchange": exchange,
            "extra_weeks": len(extra_weeks) - 1
        }
        order_id = request.env['sale.order'].sudo().create(data)

        for product_id in product_ids:
            request.env['sale.order.line'].sudo().create({
                'order_id': order_id.id,
                'rental_type': 'new_rental',
                'number_of_days': 1,
                'rental_qty': 1,
                'customer_lead': 1,
                'start_date': post.get('event_date'),
                'end_date': post.get('event_date'),
                'product_id': product_id.get('id'),
                'name': product_id.get('barcode'),
                'product_uom_qty': 1,
                'price_unit': product_id.get('price') if not post.get('exchange') or post.get(
                    'exchange') == 'false' else 0,
                'extra_weeks_dates': extra_weeks,
            })
        if len(extra_weeks) > 1:
            extra_week_product = request.env.ref('website_bridetobe.extra_week_product').sudo()
            request.env['sale.order.line'].sudo().create({
                'order_id': order_id.id,
                'product_id': extra_week_product.id,
                'name': 'Semanas Adicionales %s' % str(len(extra_weeks) - 1),
                'product_uom_qty': (len(extra_weeks) - 1) * len(product_ids),
                'price_unit': extra_week_product.list_price if post.get('exchange') == 'false' else 0
            })
        return order_id

    @http.route(['/renta/order_confirmation'], type='http', auth="public",
                methods=['GET'], website=True, csrf=True)
    def order_confirmation(self, **post):

        order_id = request.env['sale.order'].sudo().browse(int(post.get('order_id')))
        if order_id.state not in ['sale', 'done', 'cancel']:
            if order_id.action_confirm():
                order_id.action_invoice_create()
                rental_ids = request.env['sale.rental'].sudo().search([('start_order_id', '=', order_id.id)])
                modista_id = False
                if post.get('delivery_date') and post.get('delivery_time') and rental_ids:
                    test_delivery_date = '%s %s:00' % (post.get('delivery_date'), post.get('delivery_time'))
                    test_delivery_date = datetime.strptime(test_delivery_date,
                                                           DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=4)
                    if post.get('modista_id') and post.get('modista_id') != '0':
                        modista_id = int(post.get('modista_id'))
                    rental_ids.write({'test_date': test_delivery_date, 'delivery_date': test_delivery_date,
                                      'modista': modista_id, 'details': post.get('comments')})
        return request.render('website_bridetobe.order_validation', {'order_id': order_id})

    @http.route(['/search_available'], type='http', auth="public", methods=['GET'],
                website=True, csrf=True)
    def search_available(self, **post):
        return request.render('website_bridetobe.search_available', {})

    @http.route(['/search_available_calendar'], type='http', auth="public", methods=['POST'],
                website=True, csrf=True)
    def search_available_calendar(self, **post):
        error = dict()
        error_message = []
        product_barcode = post.get('product_barcode')
        product_id = request.env['product.template'].sudo().search(['|', ('barcode', '=', product_barcode),
                                                                    ('name', 'ilike', product_barcode),
                                                                    ('rented_product_id', '!=', False)])
        if not product_barcode:
            error['product_barcode'] = 'missing'
            error_message.append('Digite Codigo de Producto')
        elif not product_id:
            error['product_barcode'] = 'missing'
            error_message.append('Codigo de Producto Invalido')
        if error_message:
            error['error_message'] = error_message
            render_values = {
                'error': error
            }
            return request.render('website_bridetobe.search_available', render_values)

        render_values = {
            'product_id': product_id
        }
        return request.render('website_bridetobe.search_available_calendar', render_values)

    @http.route(['/get_events'], type='http', auth="public", methods=['POST'],
                website=True, csrf=True)
    def get_events(self, **post):
        start_date = post.get('start')
        end_date = post.get('end')
        product_id = post.get('product_id')
        sale_rental_ids = []
        product_ids = []
        for product_rental in product_id.replace('[', '').replace(']', '').split(','):
            product_ids.append(int(product_rental))
        sale_rental_search_ids = request.env['sale.rental'].sudo().search(
            [('start_date', '>=', start_date), ('start_date', '<=', end_date),
             ('rental_product_id', 'in', product_ids),
             ('state', 'not in', ('cancel', 'in'))])
        for sale_rental_id in sale_rental_search_ids:
            sale_rental_ids.append({'title': sale_rental_id.rental_product_id.barcode,
                                    'start': sale_rental_id.start_date})
        return json.dumps(sale_rental_ids)

    @http.route(['/get_next_week'], type='http', auth="none", methods=['POST'], csrf=False)
    def get_next_week(self, **post):
        event_date = datetime.strptime(post.get('event_date'), DEFAULT_SERVER_DATE_FORMAT)
        return json.dumps({"event_date": str((event_date + timedelta(days=7 * int(post.get('week_count')))).date())})
