# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.web.controllers.main import Home
from odoo import http, _
from odoo.http import request
from ...website_bridetobe.controllers.main import BridetoBe
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class BridetoBe(BridetoBe):
    update_partner_mandatory_fields = [
        ["country_id", "Debe seleccionar un Pais"],
        ["name", "Digite su nombre"],
        ["mobile", "Digite su numero de movil"],
        ["phone", "Digite su numero de Telefono"],
        ["email", "Digite su Email"],
        ["street", "Digite la Calle"],
        ["state_id", "Debe digitar su estado"],
        ["city", "Debe digitar su ciudad"]]

    mandatory_fields = ["country_id", "state_id", "name", "mobile", "phone", "email", "street", "city", "seller_code",
                        "cadera",
                        "event_place", "busto", "event_date", "cintura", "product_barcode", "vat"]

    def get_state_ids(self):
        return request.env['res.country.state'].sudo().search([])

    def validate_partner(self, post, error=dict()):
        render_values = super(BridetoBe, self).validate_partner(post, error=dict())
        render_values.update({'state_ids': self.get_state_ids()})
        print(render_values)
        return render_values

    def get_rent_values(self, view_id):
        render_values = super(BridetoBe, self).get_rent_values(view_id)
        render_values.update({'state_ids': self.get_state_ids()})
        print(render_values)
        return render_values

    def _event_data(self, post):
        order_id = super(BridetoBe, self)._event_data(post)

        if post.get('pickup') == 'true':
            pickup = True
        else:
            pickup = False

        order_id.write({"pickup": pickup})

        if pickup:
            pickup_product = request.env.ref('pickup.pickup_service').sudo()
            request.env['sale.order.line'].sudo().create({
                'order_id': order_id.id,
                'product_id': pickup_product.id,
                'name': pickup_product.name,
                'product_uom_qty': 1,
                'tax_id': False,
                'price_unit': pickup_product.list_price if not post.get('exchange') or post.get(
                    'exchange') == 'false' else 0,
            })
        print(order_id, order_id.pickup)
        return order_id
