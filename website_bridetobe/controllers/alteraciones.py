from odoo import http, _
from odoo.http import request
from datetime import datetime
from ...web_quote.controllers.main import WebQuote
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from ..controllers.main import BridetoBe


class BridetobeAlteraciones(http.Controller):
    update_partner_mandatory_fields = [
        ["country_id", "Debe seleccionar un Pais"],
        ["name", "Digite su nombre"],
        ["mobile", "Digite su numero de movil"],
        ["phone", "Digite su numero de Telefono"],
        ["email", "Digite su Email"],
        ["street", "Digite la Calle"],
        ["city", "Debe digitar su ciudad"],
        ["customer_code", "Debe digitar el Codigo del cliente"]
    ]

    event_data_mandatory_fields = [
        ['comments', "Debe agregar comentarios"],
        ['price', "Especifique el costo del la Confeccion"],
        ['details', "Debe especificar los detalles de la Confeccion"],
        ['delivery_date', "Seleccione la fecha de Entrega"],
    ]

    def update_partner_fields(self, post):
        partner_obj = request.env['res.partner']
        partner = partner_obj
        seller = request.env['hr.employee'].sudo().browse(post.get("seller"))
        error = dict()
        error_message = []

        for field_name in self.update_partner_mandatory_fields:
            if not post.get(field_name[0]):
                error[field_name[0]] = 'missing'
                error_message.append(field_name[1])
        if not error:
            if post.get("partner"):
                partner = partner_obj.sudo().browse(int(post.get("partner")))
                if post.get('name') == partner.name:
                    del (post['name'])
                partner.write(post)
            else:
                try:
                    partner = partner.sudo().create(post)
                except Exception as err:
                    error['vat'] = 'duplicate'
                    error_message.append(err[0])
        if error_message:
            error['error_message'] = error_message
        render_values = {
            'error': error,
            'partner': partner,
            'partner_temp': post,
            'country': partner.country_id,
            'product_ids': [],
            'seller': seller,
            'countries': partner.country_id.get_website_sale_countries('new'),
            'view_id': post.get('view_id'),
            'customer': True,
        }
        return render_values

    @http.route(['/alteraciones'], type='http', methods=['GET'], website=True, csrf=True, auth="user")
    def alteraciones(self):
        qweb_template, data = WebQuote().web_quote(form_action='/alteraciones/search_partner')
        return request.render('website_bridetobe.web_quote_search_partner', data)

    def _search_partner(self, post):
        qweb_template, data = WebQuote().search_partner(post=post,
                                                        template_action=[('web_quote.web_quote_partner_list',
                                                                          '/alteraciones/partner_details'),
                                                                         ('web_quote.web_quote_partner_details',
                                                                          '/alteraciones/partner_update'),
                                                                         ('web_quote.web_quote_search_partner',
                                                                          '/alteraciones/search_partner')],
                                                        search_filters=['|', ('name', 'ilike', post.get('partner_vat')),
                                                                        ('vat', '=', post.get('partner_vat'))])
        return request.render(qweb_template, data)

    @http.route(['/alteraciones/search_partner'], type='http', auth="user",
                methods=['POST'], website=True)
    def search_partner(self, **post):
        return self._search_partner(post)

    @http.route(['/alteraciones/partner_details'], type='http', auth="user",
                methods=['POST'], website=True)
    def partner_details(self, **post):
        if post.get('partner_id'):
            partner_id = request.env['res.partner'].browse(int(post.get('partner_id')))
            qweb_template, data = WebQuote().partner_details(partner_id=partner_id, partner_temp=post,
                                                             form_action='/alteraciones/partner_update')
            return request.render(qweb_template, data)
        else:
            return self._search_partner(post)

    @http.route(['/alteraciones/partner_update'], type='http', auth="user",
                methods=['POST'], website=True)
    def partner_update(self, **post):
        # data = self.update_partner_fields(post)
        qweb_template, data = WebQuote().partner_update(post=post,
                                                        mandatory_fields=self.update_partner_mandatory_fields,
                                                        template_action=[('website_bridetobe.alteraciones_quote_items',
                                                                          '/alteraciones/quote_items'),
                                                                         ('website_bridetobe.alteraciones_quote_items',
                                                                          '/alteraciones/quote_items'),
                                                                         ('web_quote.web_quote_partner_details',
                                                                          '/alteraciones/partner_update')])
        modista_ids = request.env['hr.employee'].search_read(
            [('department_id', '=', request.env.ref('website_bridetobe.modista').id)], ['name'])
        data.update({'modista_ids': modista_ids})
        return request.render(qweb_template, data)

    @http.route(['/alteraciones/quote_items'], type='http', auth="user", methods=['POST'],
                website=True, csrf=True)
    def quote_items(self, **post):
        error = WebQuote().validate_mandatory_fields(post, self.event_data_mandatory_fields)
        if post.get('modista_id') == '0':
            error['modista_id'] = 'missing'
            if 'error_message' in error:
                error['error_message'].append("Modista no Seleccionada")
            else:
                error['error_message'] = ["Modista no Seleccionada"]

        partner = request.env['res.partner'].browse(int(post.get('partner')))
        if post.get('partner'):
            partner.write({'busto': post.get('busto'),
                           'cintura': post.get('cintura'),
                           'cadera': post.get('cadera'),
                           'falda': post.get('falda')})
        modista_ids = request.env['hr.employee'].search_read(
            [('department_id', '=', request.env.ref('website_bridetobe.modista').id)], ['name'])
        render_values = {'error': error,
                         'partner_id': partner,
                         'form_method': 'post',
                         'modista_ids': modista_ids,
                         'modista_id': post.get('modista_id'),
                         'comments': post.get('comments', ''),
                         'price': post.get('price'),
                         'details': post.get('details', ''),
                         'delivery_date': post.get('delivery_date')}
        if error:
            return request.render('website_bridetobe.alteraciones_quote_items', render_values)
        else:
            render_values.update({'form_action': '/alteraciones/quote_confirmation',
                                  'readonly': True})
            return request.render('website_bridetobe.alteraciones_quote_items', render_values)

    @http.route(['/alteraciones/quote_confirmation'], type='http', auth="public",
                methods=['POST'], website=True, csrf=True)
    def order_confirmation(self, **post):
        data = {
            "partner_id": int(post.get('partner')),
            "default_start_date": post.get('delivery_date'),
            "default_end_date": post.get('delivery_date'),
            "comments": post.get('comments', ''),
            "details": post.get('details', '')
        }
        order_id = request.env['sale.order'].sudo().create(data)
        product = request.env.ref('website_bridetobe.alteracion_rental_product')
        product_id = request.env['product.product'].search([('product_tmpl_id', '=', product.id)])
        request.env['sale.order.line'].sudo().create({
            'order_id': order_id.id,
            'rental_type': 'new_rental',
            'number_of_days': 1,
            'rental_qty': 1,
            'customer_lead': 1,
            'start_date': post.get('delivery_date'),
            'end_date': post.get('delivery_date'),
            'product_id': product_id.id,
            'name': "Alteracion",
            'product_uom_qty': 1,
            'price_unit': post.get('price')
        })
        if order_id.action_confirm():
            order_id.action_invoice_create()
            order_id.action_done()
            sale_rental = request.env['sale.rental'].search([('start_order_id', '=', order_id.id)], limit=1)
            sale_rental.delivery_date = post.get('delivery_date')
            sale_rental.comments = post.get('comments', '')
            sale_rental.details = post.get('details', '')
            sale_rental.in_picking_id.unlink()
            sale_rental.modista = int(post.get('modista_id'))
            return request.redirect('/alteraciones')
