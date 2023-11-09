# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from .main import BridetoBe


class BridetoBeConfecciones(BridetoBe):
    confecciones_data_mandatory_fields = [
        ["event_place", "Debe digitar el Lugar del evento"],
        ["event_date", "Debe digitar la fecha del Evento"],
        ["c_moda", "Debe Seleccionar el modo de suministro de la Moda"],
        ["suministro_materiales", "Debe Seleccionar el modo del Suministro de los Materiales"],
        ["description", "Debe agregar una Descripcion"],
        ["tipo_confeccion", ""],
        ["color", ""],
        ["tipo", ""]
    ]

    def confecciones_update_partner(self, post):
        render_values = {}
        partner = request.env['res.partner'].sudo()
        partner_id = post.get('partner_id')
        partner_vat = post.get("vat")

        if partner_vat and not partner_id:
            partner_id = partner.search([('vat', '=', partner_vat)], limit=1)
        elif partner_id:
            partner_id = partner.browse(int(partner_id))
            customer_data = {
                'name': post.get('partner_name'),
                'mobile': post.get('mobile'),
                'phone': post.get('phone'),
                'email': post.get('email'),
                'street': post.get('street'),
                'city': post.get('city'),
                'country_id': int(post.get('country_id')) if post.get('country_id') else 62

            }
            partner_id.write(customer_data)

        render_values.update({'partner_id': partner_id})

        error = dict()
        error_message = []

        if 'search_partner' not in post:
            self.validate_required_fields(post, error, self.confecciones_data_mandatory_fields)
            self.validate_required_fields(post, error, self.update_partner_mandatory_fields)

            render_values.update({'error': error})

        return render_values

    @http.route(['/confeccion'], type='http', auth="public",
                methods=['GET'], website=True, csrf=True)
    def get_confeccion(self, **get):
        render_values = {
            'modista_ids': self.get_modista_ids(),
            'country_ids': self.get_country_ids(),
            'metric_ids': request.env['bridetobe.metric'].sudo().search([('show_web', '=', True)]),
            'metrics': {}
        }
        return request.render('website_bridetobe.web_confeccion', render_values)

    @http.route(['/confeccion'], type='http', auth="public",
                methods=['POST'], website=True, csrf=True)
    def confecciones_data(self, **post):
        render_values = post
        render_values.update({
            'modista_ids': self.get_modista_ids(),
            'country_ids': self.get_country_ids(),
            'metric_ids': request.env['bridetobe.metric'].sudo().search([('show_web', '=', True)]),
            'description': post.get('description').strip(),
            'notes': post.get('notes').strip(),
            'tela': post.get('tela').strip(),
            'materiales': post.get('materiales').strip(),
        })
        metrics = post.get('metrics', {})
        for metric in render_values:
            if 'm_' in metric:
                metrics[metric] = render_values[metric]
        render_values.update({'metrics': metrics})

        if 'search_partner' in post:
            render_values.update(self.confecciones_update_partner(render_values))
            return request.render('website_bridetobe.web_confeccion', render_values)
        else:
            render_values.update(self.confecciones_update_partner(render_values))
            if render_values.get('error'):
                return request.render('website_bridetobe.web_confeccion', render_values)
            else:
                render_values.update({'confirmation': True, 'action': '/confeccion/confeccion_data'})
                return request.render('website_bridetobe.web_confeccion', render_values)

    @http.route(['/confeccion/confeccion_data'], type='http', auth="public",
                methods=['POST'], website=True, csrf=True)
    def confecciones_validate(self, **post):
        render_values = post
        render_values.update({
            'description': post.get('description').strip(),
            'notes': post.get('notes').strip(),
            'tela': post.get('tela').strip(),
            'materiales': post.get('materiales').strip(),
            'metric_ids': request.env['bridetobe.metric'].sudo().search([('show_web', '=', True)]),
        })
        metrics = post.get('metrics', {})
        for metric in render_values:
            if 'm_' in metric:
                metrics[metric] = render_values[metric]
        render_values.update({'metrics': metrics})

        if 'back' in post:
            render_values.update({
                'modista_ids': self.get_modista_ids(),
                'country_ids': self.get_country_ids(),
                'metric_ids': request.env['bridetobe.metric'].sudo().search([('show_web', '=', True)])
            })
            render_values.update(self.confecciones_update_partner(render_values))
            render_values.update({'confirmation': False, 'action': '/confeccion'})
            return request.render('website_bridetobe.web_confeccion', render_values)
        else:
            render_values.update({'confirmation': True, 'action': '/confeccion/confeccion_data'})
            confeccion = request.env['bridetobe.confeccion'].sudo()
            confeccion_id = render_values.get('confeccion_id')

            if confeccion_id != '':
                confeccion_id = confeccion.browse(int(confeccion_id))
                confeccion_id.write({'costo': render_values.get('costo'), 'metrics': metrics})
            else:
                confeccion_id = confeccion.create(render_values.copy())
            render_values['confeccion_id'] = confeccion_id
            render_values['action'] = '/confeccion/confeccion_data/confirmation'
            return request.render('website_bridetobe.web_confeccion_confirmation', render_values)

    @http.route(['/confeccion/confeccion_data/confirmation'], type='http', auth="public",
                methods=['post'], website=True, csrf=True)
    def confecciones_confirmation(self, **post):
        partner = request.env['res.partner'].sudo()
        partner_id = post.get('partner_id')
        metrics = post.get('metrics', {})
        for metric in post:
            if 'm_' in metric:
                metrics[metric] = post[metric]
        post.update({'metrics': metrics})

        if partner_id != '':
            partner_id = partner.browse(int(partner_id))
        else:
            partner_data = {
                'name': post.get('partner_name'),
                'mobile': post.get('mobile'),
                'phone': post.get('phone'),
                'email': post.get('email'),
                'customer_code': post.get('customer_code'),
                'vat': post.get('vat'),
                'street': post.get('street'),
                'city': post.get('city'),
                'country_id': int(post.get('country_id')) if post.get('country_id') else 62
            }
            partner_id = partner.create(partner_data)
            post.update({'partner_id': partner_id.id})

        if 'back' in post:
            post.update({'confirmation': True,
                         'action': '/confeccion/confeccion_data', 'partner_id': partner_id,
                         'modista_ids': self.get_modista_ids(),
                         'country_ids': self.get_country_ids(),
                         'metric_ids': request.env['bridetobe.metric'].sudo().search([('show_web', '=', True)])})
            return request.render('website_bridetobe.web_confeccion', post)
        else:
            confeccion = request.env['bridetobe.confeccion'].sudo()
            confeccion_id = post.get('confeccion_id')
            confeccion_id = confeccion.browse(int(confeccion_id))
            confeccion_id.update({'partner_id': partner_id})
            confeccion_id.create_invoice()
            self.confirmation_materials(post)
            return request.redirect('/confeccion')

    def confirmation_materials(self, post):
        materiales = str(post.get('materiales'))
        if post.get('suministro_materiales') != 'c_tienda' and materiales != '' and post.get('enviar') != '':
            confeccion = request.env['bridetobe.confeccion'].sudo()
            partner = request.env['res.partner'].sudo().search([('id', '=', post.get('partner_id'))])
            custom_message = request.env['sale.rental.custom.message'].sudo().search(
                [('available_model_id.model_name', '=', 'bridetobe.confeccion'),
                 ('ir_model_field_id.name', '=', 'materiales')])
            message_body = custom_message.message_body
            params = [str(partner.mobile), str(partner.name), materiales]
            confeccion.post_message(message_body, custom_message, params)
