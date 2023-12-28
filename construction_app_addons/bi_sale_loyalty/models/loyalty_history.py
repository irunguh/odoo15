# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class LoyaltyHistory(models.Model):
	_name = 'loyalty.history'
	_rec_name = 'partner_id'
	_order = 'id desc'
		
	partner_id  = fields.Many2one('res.partner','Customer',required=True)
	date  =  fields.Date(default = datetime.now().date() ,string="Date")
	points = fields.Integer('Loyalty Points')
	transaction_type = fields.Selection([('receive', 'Receive'), ('send', 'Send'),('cancel','Cancel'),('invalid','Invalid')], string='Status', help='credit/debit loyalty transaction.')
	is_expired = fields.Boolean('Is Expired')
	used_from_last = fields.Boolean("Used From Last Year Points")
	payment_id = fields.Many2one('account.payment',"Payment Entry")
	payment_amount = fields.Float("Amount")
	product_id = fields.Many2one('product.product', 'Gift Product', domain="[('is_gift_product', '=', True)]")
	total_points = fields.Integer('Total Points')
	delivery_order_id = fields.Many2one('stock.picking','Delivery Order')
	extra_note = fields.Text(string="Note")
	to_be_expired = fields.Boolean("To be Expired")
	is_send_cancel = fields.Boolean("Is send cancel")
	last_year_used_cancel = fields.Boolean("last_year_used_cancel")
	total_payment_amount = fields.Float('Total Payment Amount')

    # prevent user from deleting loyalty history
	def unlink(self):
	 	raise UserError(_(
	 		'You cannot delete loyalty history for a customer.'))

