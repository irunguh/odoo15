# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def edit_line_ids(self, analytic_account_id=None, analytic_tag_ids=None, payment=None):
        ar = self.partner_id.property_account_receivable_id
        ap = self.partner_id.property_account_payable_id
        if payment:
            ar = payment.partner_id.property_account_receivable_id
            ap = payment.partner_id.property_account_payable_id
            analytic_account_id = payment.analytic_account_id
            analytic_tag_ids = payment.analytic_tag_ids

        for rec in self.line_ids:
            if payment:
                if payment.payment_type == 'inbound':
                    if rec.credit > 0:
                        rec.analytic_account_id = payment.analytic_account_id
                        rec.analytic_tag_ids = payment.analytic_tag_ids

                if payment.payment_type == 'outbound':
                    if rec.debit > 0:
                        rec.analytic_account_id = payment.analytic_account_id
                        rec.analytic_tag_ids = payment.analytic_tag_ids
            else:
                if rec.account_id.id == ar.id or rec.account_id.id == ap.id:
                    rec.analytic_account_id = analytic_account_id.id
                    rec.analytic_tag_ids = analytic_tag_ids.ids


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    def action_post(self):
        self.move_id.sudo().edit_line_ids(self.analytic_account_id, self.analytic_tag_ids, self)
        self.move_id._post(soft=False)
