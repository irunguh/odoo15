# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class ResConfigSettingsInherit(models.TransientModel):
	_inherit = 'res.config.settings'

	point_cal = fields.Integer(string='Point Value',default=5)
	year_end_Date = fields.Date('Closing Year Date')
	grace_period_Date = fields.Date('Grace Period Date')
	#####
	point_redeem_value = fields.Integer(string='Point Redeem Value')

	# products and points configuration

	@api.model
	def get_values(self):
		res = super(ResConfigSettingsInherit, self).get_values()
		res.update(point_cal = int(self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.point_cal')))
		res.update(year_end_Date = self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.year_end_Date'))
		res.update(grace_period_Date = self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.grace_period_Date'))
		#
		res.update(point_redeem_value=int(self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.point_redeem_value')))
		return res

	def set_values(self):
		super(ResConfigSettingsInherit, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('bi_sale_loyalty.point_cal', int(self.point_cal))
		self.env['ir.config_parameter'].sudo().set_param('bi_sale_loyalty.year_end_Date', self.year_end_Date)
		self.env['ir.config_parameter'].sudo().set_param('bi_sale_loyalty.grace_period_Date', self.grace_period_Date)
		self.env['ir.config_parameter'].sudo().set_param('bi_sale_loyalty.point_redeem_value', int(self.point_redeem_value))


class ResetLoyaltyPoints(models.Model):
	
	_name = "reset.points"

	def _cron_loyalty_history(self) :
		current_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d").date()

		point_cal = int(self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.point_cal'))
		year_end_Date = self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.year_end_Date')
		grace_period_Date = self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.grace_period_Date')

		final_end_date = None
		final_grace_date = None
		consider_date = None

		if year_end_Date :
			year_end_Date  = datetime.strptime(year_end_Date,  "%Y-%m-%d").date()
			final_end_date = year_end_Date + timedelta(days=1)
			consider_date = final_end_date

		if year_end_Date and grace_period_Date :
			grace_period_Date = datetime.strptime(grace_period_Date, "%Y-%m-%d").date()
			final_grace_date = grace_period_Date + timedelta(days=1)
			if final_grace_date > final_end_date :
				consider_date = final_grace_date

		
		if final_end_date and  current_date == final_end_date :
			partner = self.env['res.partner'].search([('loyalty_points','>',0)])
			if final_grace_date > final_end_date :
				for i in partner:
					for lines in i.loyalty_history_ids :
						if lines.to_be_expired == False:
							lines.write({'to_be_expired':True})


		if consider_date and  current_date == consider_date :
			partner = self.env['res.partner'].search([('loyalty_points','>',0)])
			for i in partner:
				if i.last_yr_loyalty_points > 0:				
					vals = {
						'partner_id': i.id,
						'date' : datetime.now().date() ,
						'points': i.last_yr_loyalty_points,
						'transaction_type' : 'send',
						'total_points': i.loyalty_points,
						'used_from_last' : True,
						'extra_note': 'Deduction of Expired points',
						'total_payment_amount' : 0.0,
					}
					loyalty_history = self.env['loyalty.history'].create(vals)

				for lines in i.loyalty_history_ids :
					if lines.is_expired == False and lines.to_be_expired:
						lines.write({'is_expired':True,
									'to_be_expired':False})