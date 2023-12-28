# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)
class InheritCustomer(models.Model):
	
	_inherit = "res.partner"

	loyalty_points = fields.Integer('Loyalty Points',compute='calculate_loyalty_points',store=True)
	last_yr_loyalty_points = fields.Integer('Last Loyalty Points',compute='calculate_loyalty_points',store=True)
	current_yr_loyalty_points = fields.Integer('Current Loyalty Points',compute='calculate_loyalty_points',store=True)
	loyalty_history_ids = fields.One2many('loyalty.history','partner_id',string="Loyalty History",readonly=True)
	total_amount = fields.Float("Total Amount",compute='calculate_loyalty_points')

	@api.depends('loyalty_history_ids')
	def calculate_loyalty_points(self):
		customer_points = 0
		total_amount1 = 0
		for partner in self:
			# earned points
			browse_points = self.env['loyalty.history'].search(
				[('partner_id', '=', partner.id), ('transaction_type', '=', 'receive')])

			for p in browse_points:
				customer_points += p.points
				total_amount1 += p.payment_amount
			# lets now set this on customer card
			_logger.info("Debug::: Points Computed from History {0}".format(customer_points))
			partner.loyalty_points = customer_points
			partner.total_amount = total_amount1
		# TODO - commented out this method of points calculation
		# now_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").date()
		# current_date = str(now_date.day) +"-"+str(now_date.month)
		# current_year = str(now_date.year)
		#
		# for partner in self:
		# 	total = 0
		# 	current = 0
		# 	last = 0
		# 	last_used = 0
		# 	total_amount1 = 0
		# 	for rec in partner.loyalty_history_ids:
		# 		if not  rec.is_expired:
		# 			if rec.to_be_expired :
		# 				if rec.transaction_type == 'receive' :
		# 					last += rec.points
		# 				else:
		# 					if rec.is_send_cancel :
		# 						last += rec.points
		# 					else:
		# 						last -= rec.points
		# 			else:
		# 				if rec.transaction_type == 'receive' :
		# 					current += rec.points
		# 				else:
		# 					if rec.transaction_type == 'send' and rec.used_from_last:
		# 						last_used += rec.points
		# 					elif rec.transaction_type == 'cancel' and rec.last_year_used_cancel:
		# 						#last_used -= rec.points
		# 						_logger.info('Debug: Cancel points ignored! {0}'.format(rec.points))
		# 					else:
		# 						if rec.is_send_cancel :
		# 							current += rec.points
		# 						else:
		# 							current -= rec.points
		#
		# 		if rec.transaction_type == 'receive' :
		# 			total_amount1 += rec.payment_amount
		# 		elif rec.transaction_type == 'send' :
		# 			total_amount1 -= rec.payment_amount
		# 		else:
		# 			if rec.is_send_cancel :
		# 				total_amount1 += rec.payment_amount
		# 			else:
		# 				total_amount1 -= rec.payment_amount
		#
		# 	partner.current_yr_loyalty_points = current
		# 	total = current
		# 	last = last - last_used
		# 	if last > 0 :
		# 		partner.last_yr_loyalty_points = last
		# 		total = current + last
		# 	# if total < 0 :
		# 	# 	total = 0
		# 	partner.loyalty_points = total
		# 	partner.total_amount = total_amount1



