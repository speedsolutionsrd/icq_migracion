from odoo import http
from odoo.http import request
from ...website_bridetobe.controllers.main import BridetoBe
from ...website_bridetobe.controllers.web_quote import BridetobeWebQuote

class BridetoBe(BridetoBe):

    def _event_data(self, post):
        template, render_values = super(BridetoBe, self)._event_data(post)
        render_values.update({'seller':request.env['hr.employee'].sudo().browse(int(render_values.get("seller")))})
        return (template, render_values)

    @http.route(['/search_available'], type='http', auth="public", methods=['POST'],website=True, csrf=True)
    def search_available(self, **post):
        return request.render('website_bridetobe.search_available', {})

class WebQuote(BridetobeWebQuote):
    @http.route(['/web_quote'], type='http', auth="user",methods=['POST'], website=True)
    def web_quote(self, **post):
        qweb_template, data = WebQuote().web_quote()
        return request.render(qweb_template, data)
