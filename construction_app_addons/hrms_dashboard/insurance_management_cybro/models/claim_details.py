# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models, _


class ClaimDetails(models.Model):
    _name = 'claim.details'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.parent.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('insurance', 'Insurance Approval'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    name = fields.Char(string='Name', required=True, copy=False,
                       readonly=True, index=True, default=lambda self: _('New'))
    name_2 = fields.Char(
        string='Name 2', required=True, copy=False, readonly=True, index=True,
        default=lambda self: _('New'))
    insurance_id = fields.Many2one('insurance.details', required=False,
                                   domain=[('state', '=', 'confirmed')],
                                   help="Confirmed orders can be selected")
    partner_id = fields.Many2one('res.partner',string='Customer',tracking=True, required=True,domain=[('is_a_customer', '=', True)])
    policy_id = fields.Many2one(related='insurance_id.policy_id',
                                string='Policy', readonly=False)
    place_of_incident = fields.Char(string="Place of Incident",required=True)

    user_id = fields.Many2one(
        'res.users', string='Created By', index=True, tracking=2, default=lambda self: self.env.user, required=True)
    approved_by = fields.Many2one('res.users',string='Approved by')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    amount = fields.Monetary(related='insurance_id.amount', string='Amount Insured')
    date_claimed = fields.Datetime(
        tracking=True,string='Date Applied', default=fields.Date.context_today, required=True)
    reported_on = fields.Date(
        tracking=True, string='Date Reported', default=fields.Date.context_today, required=True)
    invoice_id = fields.Many2one('account.move', string='Invoiced',
                                 readonly=True, copy=False)
    note_field = fields.Html(string='Comment')

    incident_type = fields.Selection([('screen_repair','Screen Breakage / Repair'),('theft','Phone Theft')],
                                  string='Nature of Incident',required=True,tracking=True)

    def action_insurance(self):
        return self.write({'state': 'insurance'})
    # print out
    def action_print(self):
        return True

    def action_reject(self):
        return self.write({'state': 'reject'})

    # Actions
    # Confirm an order - This means you have checked the data
    def action_confirm(self):
        return self.write({'state': 'confirm'})

    # approve request
    def action_approve(self):
        return self.write({'state': 'approved', 'approved_by': self.env.user})

    # cancel request
    def action_cancel(self):
            return self.write({'state': 'cancel'})
    # draft request
    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'claim.details') or 'New'
        return super(ClaimDetails, self).create(vals)

    def action_create_bill(self):
        if not self.invoice_id:
            invoice_val = self.env['account.move'].sudo().create({
                'move_type': 'in_invoice',
                'invoice_date': fields.Date.context_today(self),
                'partner_id': self.partner_id.id,
                'invoice_user_id': self.env.user.id,
                'claim_id': self.id,
                'invoice_origin': self.name,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Invoice For Insurance Claim',
                    'quantity': 1,
                    'price_unit': self.amount,
                    'account_id': 41,
                })],
            })
            self.invoice_id = invoice_val
