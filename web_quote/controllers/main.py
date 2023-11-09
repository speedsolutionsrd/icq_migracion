from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WebQuote(http.Controller):
    def web_quote(self, form_action='/web_quote/search_partner'):
        print("form_action",form_action)
        return ('web_quote.web_quote_search_partner',
                {'error': dict(),
                 'partner_temp': dict(),
                 'form_action': form_action,
                 'form_method': 'post'})

    def validate_mandatory_fields(self, post, mandatory_fields):
        error = dict()
        error_message = []
        for field_name in mandatory_fields:
            if not post.get(field_name[0]):
                error[field_name[0]] = 'missing'
                error_message.append(field_name[1])
        if error_message:
            error['error_message'] = error_message
        return error

    def search_partner(self, post, search_filters=[],
                       template_action=[('web_quote.web_quote_partner_list', '/web_quote/partner_details'),
                                        ('web_quote.web_quote_partner_details', '/web_quote/partner_update'),
                                        ('web_quote.web_quote_search_partner', '/web_quote/search_partner')],
                       ):
        print("form_action1",form_action)
        error = dict()
        error_message = []
        partner_ids = []
        form_action = ''
        qweb_template = False
        if post.get('partner_vat', False):
            partner_ids = request.env['res.partner'].search(search_filters)

        if len(partner_ids) > 1:
            qweb_template = template_action[0][0]
            form_action = template_action[0][1]
        elif len(partner_ids) == 1:
            qweb_template = template_action[1][0]
            form_action = template_action[1][1]
        else:
            error['partner_vat'] = 'missing'
            error_message.append('Cliente no Existe')
            error['error_message'] = error_message
            if post.get('submit') == 'new':
                qweb_template = template_action[1][0]
                form_action = template_action[1][1]
                error = dict()
                post['vat'] = post.get('partner_vat')
                partner_ids = request.env['res.partner']
            elif post.get('submit') == 'confirm':
                qweb_template = template_action[2][0]
                form_action = template_action[2][1]
        
        return (qweb_template,
                {'error': error,
                 'partner_temp': post,
                 'country_ids': request.env['res.country'].sudo().search([]),
                 'form_action': form_action,
                 'form_method': 'post',
                 'partner_id': partner_ids,
                 'partner_ids': partner_ids})

    def partner_details(self, partner_id, partner_temp, form_action='/web_quote/partner_update'):
        print("form_action2",form_action)
        return ('web_quote.web_quote_partner_details',
                {'error': dict(),
                 'form_action': form_action,
                 'form_method': 'post',
                 'country_ids': request.env['res.country'].sudo().search([]),
                 'partner_id': partner_id,
                 'partner_temp': partner_temp
                 })

    def partner_update(self, post, mandatory_fields,
                       template_action=[('web_quote.quote_items', '/web_quote/quote_items'),
                                        ('web_quote.quote_items', '/web_quote/quote_items'),
                                        ('web_quote.web_quote_partner_details', '/web_quote/partner_update')]):
        print("form_action3",form_action)
        error = dict()
        error_message = []
        partner_obj = request.env['res.partner']
        partner_id = partner_obj
        error = self.validate_mandatory_fields(post, mandatory_fields)
        if not error:
            if post.get("partner_id"):
                partner_id = partner_obj.browse(int(post.get("partner_id")))
                if post.get('name') == partner_id.name:
                    del (post['name'])
                partner_id.write(post)
                qweb_template = template_action[0][0]
                form_action = template_action[0][1]
            else:
                try:
                    partner_obj.validate_rnc_cedula(post.get('vat'))
                    partner_id = partner_obj.create(post)
                    post['partner_id'] = partner_id.id
                    error = dict()
                    qweb_template = template_action[1][0]
                    form_action = template_action[1][1]
                except Exception as err:
                    error['vat'] = 'duplicate'
                    error['customer_code'] = 'duplicate'
                    error_message.append(err[0])
                    error['error_message'] = error_message
                    qweb_template = template_action[2][0]
                    form_action = template_action[2][1]
        else:
            error['error_message'] = error_message
            qweb_template = template_action[2][0]
            form_action = template_action[2][1]
        return (qweb_template,
                {'error': error if not post.get('submit', False) else dict(),
                 'form_action': form_action,
                 'form_method': 'post',
                 'country_ids': request.env['res.country'].sudo().search([]),
                 'partner_id': partner_id,
                 'partner_temp': post,
                 'product_ids': dict()})

    def quote_items(self, post, mandatory_fields,
                    actions=['/web_quote/quote_items', '/web_quote/quote_confirmation'],
                    templates=['web_quote.quote_items', 'web_quote.quote_confirmation']):
        print("form_action4",form_action)
        partner = request.env['res.partner'].browse(int(post.get("partner")))
        render_values = dict()

        error = dict()
        product_ids = []
        product_valid = []
        qweb_template = ""
        if post.get('item_code') and post.get('product_barcode'):
            product_barcode = post.get('product_barcode') + ',' + str(post.get('item_code'))
        elif not post.get('item_code') and post.get('product_barcode'):
            product_barcode = str(post.get('product_barcode'))
        else:
            product_barcode = str(post.get('item_code'))
        if post.get('event_date') and post.get('event_place'):
            for code in product_barcode.split(','):
                product = request.env['product.template'].sudo().search([('barcode', '=', code),
                                                                         ('rented_product_id', '!=', False)])
                if product:
                    date_start = datetime.strptime(post.get('event_date'),
                                                   DEFAULT_SERVER_DATE_FORMAT)
                    date_end = datetime.strptime(post.get('event_date'),
                                                 DEFAULT_SERVER_DATE_FORMAT)
                    product_availability = request.env['sale.rental'].sudo().search(
                        [('rental_product_id', '=', product.id),
                         ('start_date', '<=', datetime.strftime(date_end, DEFAULT_SERVER_DATE_FORMAT)),
                         ('start_date', '>=', datetime.strftime(date_start, DEFAULT_SERVER_DATE_FORMAT)),
                         ('state', '!=', 'cancel')])
                    if product_availability:
                        product_barcode = product_barcode.replace(product.barcode, '')
                        error['error_message'] = [
                            u''.join(("Articulo ", product.name, "no esta disponible")).encode('utf-8')]
                    elif product.barcode not in product_valid:
                        product_valid.append(product.barcode)
                        product_id = request.env['product.product'].search([('product_tmpl_id', '=', product.id)])
                        product_ids.insert(0, {"barcode": product.barcode,
                                               "name": product.name,
                                               "image": product.image,
                                               "price": product.list_price,
                                               "id": product_id.id})
                    else:
                        product_barcode = product_barcode.replace(product.barcode + ',', '', 1)
                        error['error_message'] = [
                            u''.join(("El articulo ", product.name, " ya fue agregado a la orden")).encode('utf-8')]
                else:
                    if code == post.get('item_code'):
                        error['error_message'] = ["Codigo de Articulo Invalido"]

            if post.get('submit') == 'get_item':
                qweb_template = templates[0]
            elif post.get('submit') == 'validate':
                error = self.validate_mandatory_fields(post, mandatory_fields)
                error_message = []
                if product_barcode:
                    if not request.env['product.template'].sudo().search(
                            [('barcode', 'in', post.get('product_barcode').split(","))]):
                        error['product_barcode'] = 'missing'
                        error_message.append('No ha Seleccionado Productos')
                        error['error_message'] = error_message
                else:
                    error['product_barcode'] = 'missing'
                    error_message.append('No ha Seleccionado Productos')
                    error['error_message'] = error_message
                if error:
                    qweb_template = templates[0]
                    render_values['form_action'] = actions[0]
                else:
                    data = {
                        "partner_id": int(post.get('partner')),
                        "event_date": post.get('event_date'),
                        "event_place": post.get('event_place'),
                        "busto": post.get('busto'),
                        "cintura": post.get('cintura'),
                        "cadera": post.get('cadera'),
                        "default_start_date": datetime.strptime(post.get('event_date'),
                                                                DEFAULT_SERVER_DATE_FORMAT),
                        "default_end_date": post.get('event_date'),
                        "comments": post.get('comments', '')
                    }
                    order_id = request.env['sale.order'].sudo().create(data)
                    render_values.update({'order': order_id})
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
                            'name': product_id.get('name'),
                            'product_uom_qty': 1,
                            'price_unit': product_id.get('price')
                        })
                    render_values['form_action'] = actions[1]
                    qweb_template = templates[1]
        else:
            error = self.validate_mandatory_fields(post, mandatory_fields)
            qweb_template = templates[0]
        render_values.update({'error': error,
                              'partner_id': partner,
                              'country': partner.country_id,
                              'countries': request.env['res.country'].sudo().search([]),
                              'product_ids': product_ids,
                              'product_barcode': product_barcode,
                              'event_date': post.get('event_date'),
                              'event_place': post.get('event_place'),
                              'form_method': 'post',
                              'comments': post.get('comments', '')})
        return (qweb_template, render_values)

    @http.route(['/web_quote/quote_confirmation'], type='http', auth="public",
                methods=['POST'], website=True, csrf=True)
    def order_confirmation(self, **post):
        order_id = request.env['sale.order'].sudo().browse(int(post.get('order')))
        if post.get('submit') == 'print':
            return request.redirect('/report/pdf/sale.report_saleorder/%s' % order_id.id)
        elif post.get('submit') == 'email':
            if order_id.force_quotation_send():
                return request.redirect('/web_quote')
        else:
            return request.redirect('/web_quote')
