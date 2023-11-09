from odoo import http
from odoo.http import request
from ...web_quote.controllers.main import WebQuote


class BridetobeWebQuote(http.Controller):
    update_partner_mandatory_fields = [
        ["country_id", "Debe seleccionar un Pais"],
        ["name", "Digite su nombre"],
        ["mobile", "Digite su numero de movil"],
        ["phone", "Digite su numero de Telefono"],
        ["vat", "Digite RNC / Cedula"],
        ["email", "Digite su Email"],
        ["street", "Digite la Calle"],
        ["city", "Debe digitar su ciudad"],
        ["customer_code", "Debe digitar el Codigo del cliente"]
    ]

    event_data_mandatory_fields = [
        ["cadera", "Debe digitar la medida de la Cadera"],
        ["event_place", "Debe digitar el Lugar del evento"],
        ["busto", "Debe digitar la medida del Busto"],
        ["event_date", "Debe digitar la fecha del Evento"],
        ["cintura", "debe digitar la medida de la Cintura"]]

    @http.route(['/web_quote'], type='http', auth="user",
                methods=['GET'], website=True)
    def web_quote(self, **get):
        qweb_template, data = WebQuote().web_quote()
        return request.render(qweb_template, data)

    @http.route(['/web_quote/search_partner'], type='http', auth="user",
                methods=['POST'], website=True)
    def search_partner(self, **post):
        qweb_template, data = WebQuote().search_partner(post=post,
                                                        search_filters=['|', ('name', 'ilike', post.get('partner_vat')),
                                                                        ('vat', '=', post.get('partner_vat'))])
        return request.render(qweb_template, data)

    @http.route(['/web_quote/partner_details'], type='http', auth="user",
                methods=['POST'], website=True)
    def partner_details(self, **post):
        partner_id = request.env['res.partner'].browse(int(post.get('partner_id')))
        qweb_template, data = WebQuote().partner_details(partner_id=partner_id, partner_temp=post)
        return request.render(qweb_template, data)

    @http.route(['/web_quote/partner_update'], type='http', auth="user",
                methods=['POST'], website=True)
    def partner_update(self, **post):
        qweb_template, data = WebQuote().partner_update(post=post,
                                                        mandatory_fields=self.update_partner_mandatory_fields,
                                                        template_action=[
                                                            ('website_bridetobe.quote_items', '/web_quote/quote_items'),
                                                            ('website_bridetobe.quote_items', '/web_quote/quote_items'),
                                                            ('web_quote.web_quote_partner_details',
                                                             '/web_quote/partner_update')])
        return request.render(qweb_template, data)

    @http.route(['/web_quote/quote_items'], type='http', auth="user", methods=['POST'],
                website=True, csrf=True)
    def quote_items(self, **post):
        if post.get('partner_id'):
            partner = request.env['res.partner'].browse(int(post.get('partner_id')))
            partner.write({'busto': post.get('busto'),
                           'cintura': post.get('cintura'),
                           'cadera': post.get('cadera'),
                           'falda': post.get('falda')})
        qweb_template, data = WebQuote().quote_items(post=post, mandatory_fields=self.event_data_mandatory_fields)
        if qweb_template != 'web_quote.quote_confirmation':
            qweb_template = 'website_bridetobe.quote_items'
        return request.render(qweb_template, data)
