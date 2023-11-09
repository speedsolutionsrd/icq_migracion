# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import time, date, datetime, timedelta
from odoo.exceptions import ValidationError

class bridetobeVestidores(models.Model):
    _name = 'rentq.vestidores'
    
    name = fields.Char(string='Codigo de Vestidor', required=True)
    status = fields.Selection([('enabled', 'Habilitado'),
                               ('disabled', 'Deshabilitado')], string='Estatus',
                              default="disabled",
                              required=True)
    description = fields.Text()
    occupation = fields.Boolean(string='Ocupación', default=False, copy=False)
    time_elapsed_dressing_room = fields.Char(compute='_compute_time_elapsed_dressing_room', string='tiempo transcurrido', readonly=True)

    @api.model
    @api.depends('write_date')
    def _compute_time_elapsed_dressing_room(self):
        write_date = self.write_date.split(' ')[1]
        today = datetime.today().strftime('%H:%M:%S')
        h1 = datetime.strptime(write_date, "%H:%M:%S")
        h2 = datetime.strptime(today, "%H:%M:%S")
        resultado = str(h2 - h1)
        if len(resultado) > 8:
            self.time_elapsed_dressing_room = "23:59:59"
        else:
            self.time_elapsed_dressing_room = str(h2 - h1)
