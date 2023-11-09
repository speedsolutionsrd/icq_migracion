from odoo import http
from odoo.http import request


class Pickup(http.Controller):
    @http.route(['/pickup'], type='http', auth="user", website=True)
    def index(self, **kw):
        delivery = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        print(delivery)
        pickups = request.env['pickup.pickup'].search([('status', '=', 'pending'), ('delivery_id', '=', delivery.id)])
        pickup_id = request.env['pickup.pickup'].search([('id', '=', kw.get('pickup_id'))])


        if 'try' in kw:
            return request.render('pickup.pickup_try_template', {'pickup_id': pickup_id.id})
        elif 'pickup' in kw:
            vals = {'pickup_id': pickup_id.id, 'delivery_id': delivery.id, 'status': 'pickup'}
            request.env['pickup.attempt'].create(vals)
            return request.redirect('/pickup')
        else:
            pass

        render_values = {'pickups': pickups}
        return request.render('pickup.pickup_template', render_values)

    @http.route(['/pickup/try'], type='http', auth="user", website=True)
    def pickup_try(self, **kw):
        pickup_id = request.env['pickup.pickup'].search([('id', '=', kw.get('pickup_id'))])
        delivery = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if 'send' in kw:
            vals = {'pickup_id': pickup_id.id, 'delivery_id': delivery.id,
                    'reason': kw.get("reason"), 'status': 'try'}
            pickup_id.write({'status': 'try', 'route_id': False, 'delivery_id': False})
            request.env['pickup.attempt'].create(vals)
            return request.redirect('/pickup')
        return request.render('pickup.pickup_try_template', {})
