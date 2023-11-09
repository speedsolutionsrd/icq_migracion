from odoo import http, _
from odoo.http import request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import json


class PoxboxSend(http.Controller):

    # @http.route(['/shop'], type='http', auth="public", methods=['GET'], website=True)
    @http.route('/posbox_connect', type='http', auth="user", methods=['GET'], website=True,)
    def posbos_connect(self, **get):
        print ("=====================================")
        print (get)
        # employee_obj = request.registry.get('hr.employee')
        # employee_id = employee_obj.search(request.cr, request.session.uid, [('user_id', '=', request.session.uid)], context=request.context)
        return request.redirect('/web?debug=#view_type=form&model=posbox.print&action='+str(request.env.ref('posbox_send.action_posbox_print').id))

    # @http.route(['/confecciones/confeccion_data/confirmation'], type='http', auth="public",
    #             methods=['POST'], website=True, csrf=True)
    # def confecciones_confirmation(self, **post):
    #     return request.redirect('/confecciones')