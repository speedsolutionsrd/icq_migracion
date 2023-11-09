# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from werkzeug import exceptions
from odoo.http import Controller, route, request
import base64


class ReportController(Controller):

    @route(['/invoice/<converter>/<docid>'], type='http', auth='public', website=True)
    def report_routes(self, docid=None, converter=None, **data):
        report_obj = request.env['report']
        context = dict(request.env.context)
        try:
            docids = base64.b64decode(docid)
            if converter == 'html':
                html = report_obj.sudo().with_context(context).get_html(int(docids), "account.report_invoice",
                                                                        data=data)
                return request.make_response(html)
            elif converter == 'pdf':
                pdf = report_obj.sudo().with_context(context).get_pdf(int(docids), "account.report_invoice", data=data)
                pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
                return request.make_response(pdf, headers=pdfhttpheaders)
            else:
                raise exceptions.HTTPException(description='Converter %s not implemented.' % converter)
        except:
            raise exceptions.HTTPException(description='Invalid Invoice URL.')
