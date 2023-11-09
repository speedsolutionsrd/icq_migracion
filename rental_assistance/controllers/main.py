# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.web.controllers.main import Home
from odoo import http, _
from odoo.http import request


def get_next(sequence, assistance_ids):
    if sequence and sequence < len(assistance_ids):
        active_assistance_id = assistance_ids[sequence]
        sequence += 1
    else:
        active_assistance_id = assistance_ids[0]
        sequence = 1
    return (sequence, active_assistance_id)


class Assistance(http.Controller):

    @http.route(['/assistance'], type='http', auth="user", website=True)
    def get_assistance(self, **kwargs):
        assistance = request.env['assistance.assistance'].sudo()
        assistance_ids = assistance.search([], order='sequence ASC')
        error = {}
        active_assistance_id = assistance
        counter = kwargs.get('counter')
        if counter:
            counter = int(counter)
        else:
            counter = 1

        sequence = int(kwargs.get('sequence')) if kwargs.get('sequence') else 1
        if 'active_assistance_id' in kwargs:
            active_assistance_id = assistance.browse(int(kwargs.get('active_assistance_id')))
        if 'available' in kwargs:

            request.env['sick.sick'].create({'employee_id': active_assistance_id.employee_id.id,
                                             'reason': kwargs.get('reason'),
                                             })
            sequence, active_assistance_id = get_next(sequence, assistance_ids)
        elif 'next' in kwargs:
            if counter <= 3:
                counter += 1
        elif 'sick' in kwargs:
            if not kwargs.get('reason'):
                error['reason'] = 'Debe especificar el motivo de no asistencia'
            else:
                counter = 0
                request.env['sick.sick'].create({'employee_id': active_assistance_id.employee_id.id,
                                                 'type_indisposition': 'sick',
                                                 'reason': kwargs.get('reason'),
                                                 })
                sequence, active_assistance_id = get_next(sequence, assistance_ids)
        elif 'unavailable' in kwargs:
            counter = 0
            request.env['sick.sick'].create({'employee_id': active_assistance_id.employee_id.id,
                                             'type_indisposition': 'unavailable',
                                             'reason': kwargs.get('reason'),
                                             })
            sequence, active_assistance_id = get_next(sequence, assistance_ids)

        render_values = {
            'assistance_ids': assistance_ids,
            'active_assistance_id': active_assistance_id or assistance_ids[0] if assistance_ids else assistance,
            'sequence': sequence,
            'counter': counter,
            'error': error
        }
        if assistance_ids:
            return request.render('rental_assistance.assistance', render_values)
        else:
            return request.redirect(
                '/web#action=%s' % request.env.ref('rental_assistance.action_assistance_template').id)
