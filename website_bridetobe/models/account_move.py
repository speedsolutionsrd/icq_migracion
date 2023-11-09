# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_cancel(self):
        if self.env.user.has_group('website_bridetobe.bridetobe_caja_group'):
            raise ValidationError("No tiene Permisos para Cancelar Asientos")
        else:
            return super(AccountMove, self).button_cancel()

class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self):
        if self.env.user.has_group('website_bridetobe.bridetobe_caja_group'):
            raise ValidationError("No tiene Permisos")
        else:
            return super(AccountMove, self).reverse_moves()

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def remove_move_reconcile(self):

        if self.env.user.has_group('website_bridetobe.bridetobe_caja_group'):
            raise ValidationError("No tiene Permisos para Romper Conciliacion")
        else:
            return super(AccountMoveLine, self).remove_move_reconcile()
