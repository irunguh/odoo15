# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    def _create_payment_vals_from_wizard(self):
        #print("10")
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        move_id = self.env['account.move'].browse(self.env.context.get('active_id'))
        move_id.edit_line_ids(self.analytic_account_id, self.analytic_tag_ids, payment=None)
        res.update({
            'analytic_account_id': self.analytic_account_id.id or False,
            'analytic_tag_ids': self.analytic_tag_ids.ids or False,
        })
        return res
