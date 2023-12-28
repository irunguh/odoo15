# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, datetime

class history_report_wiz(models.TransientModel):

	_name='history.report.wizard'

	start_dt = fields.Date('Start Date', required = True)
	end_dt = fields.Date('End Date', required = True)
	customer_ids = fields.Many2many('res.partner',string="Customers")
	status = fields.Selection([('all', 'All'),('receive', 'Receive'), ('send', 'Send'),('cancel','Cancel')], string='Status',default='all')
	product_ids = fields.Many2many('product.product',string="Products", domain="[('is_gift_product', '=', True)]")

	def history_generate_report(self):
		return self.env.ref('bi_sale_loyalty.action_history_report').report_action(self)


class HistoryReport(models.AbstractModel):

	_name='report.bi_sale_loyalty.report_loyalty_history'
	
	def _get_report_values(self, docids, data=None):
		history_rec = self.env['history.report.wizard'].browse(docids)
		main_data_dict = {} 
		history_data = []
		product_filter = []
		partner_filter = []

		# domain = [('date','>=',history_rec.start_dt),('date','<=',history_rec.end_dt),('is_expired','=',False)]
		domain = [('date','>=',history_rec.start_dt),('date','<=',history_rec.end_dt)]


		if history_rec.status and history_rec.status != 'all':
			domain += [('transaction_type','=',history_rec.status)]

		if history_rec.customer_ids : 
			domain += [('partner_id','in',history_rec.customer_ids.ids)]
			for i in history_rec.customer_ids:
				partner_filter.append(i.name)

		if history_rec.product_ids:
			domain += [('product_id','in',history_rec.product_ids.ids)]
			for i in history_rec.product_ids:
				product_filter.append(i.name)

		
		
		history_summary = self.env['loyalty.history'].search(domain,order="id asc")

		loaylty_data = {}
		if history_summary:
			for line in history_summary:
					# if not line.extra_note == 'Deduction of Expired points' :
					partner = line.partner_id.name
					line_status = ''
					if line.transaction_type  == 'send':
						line_status = 'Send'
					if line.transaction_type  == 'receive':
						line_status = 'Receive'
					if line.transaction_type  == 'cancel':
						line_status = 'Cancel'

					current_payment_total = line.payment_amount
					bet_points = line.points
					if line.transaction_type in ['send','cancel'] :
						if not line.is_send_cancel :
							current_payment_total = -line.payment_amount
							bet_points = -line.points

					if partner in loaylty_data:
						data = loaylty_data[partner]['data']
						temp_total  =  loaylty_data[partner]['current_payment_total']
						temp_total += current_payment_total

						temp_points = loaylty_data[partner]['bet_points']
						temp_points += bet_points

						data.append({
							'status': line_status,
							'product': line.product_id.name,
							'customer': line.partner_id.name,
							'payment_id':line.payment_id.name,
							'date' :line.date ,
							'points': line.points,
							'payment_amount' : line.payment_amount,
							'total_points': line.total_points
						})
						loaylty_data[partner].update({
							'data' : data,
							'current_payment_total': temp_total,
							'bet_points' : temp_points,
						})
					else:
						
						start_points = 0
						start_payment_amount = 0.0
						start_points_data = self.env['loyalty.history'].search([('date','<',history_rec.start_dt),('partner_id','=',line.partner_id.id)],order="id asc")
						if start_points_data:
							start_points = start_points_data[-1].total_points
						start_payment_data = self.env['loyalty.history'].search([('date','<',history_rec.start_dt),('total_payment_amount','!=',0),('partner_id','=',line.partner_id.id)],order="id asc")
						if start_payment_data:
							start_payment_amount= start_payment_data[-1].total_payment_amount
						loaylty_data.update({ partner : {
							'name' :partner,
							'points' : line.partner_id.loyalty_points,
							'start_points' : start_points,
							'bet_points' : bet_points,
							'amount_total':line.partner_id.total_amount,
							'start_payment_amount' : start_payment_amount,
							'current_payment_total' :current_payment_total,
							'data' : [{
								'status': line_status,
								'product': line.product_id.name,
								'customer': line.partner_id.name,
								'payment_id':line.payment_id.name,
								'date' :line.date ,
								'points': line.points,
								'payment_amount' : line.payment_amount,
								'total_points': line.total_points
							}]
						}})

			loyalty_history = list(loaylty_data.values())
			parnters_list = ', '.join(map(str,partner_filter) )
			products_list = ', '.join(map(str,product_filter) )

			return {
				'status': history_rec.status,
				'products': history_rec.product_ids,
				'customers': history_rec.customer_ids,
				'loyalty_history' : loyalty_history,
				'start_dt' : history_rec.start_dt,
				'end_dt' : history_rec.end_dt,
				'partner_filter' : parnters_list, 
				'product_filter' : products_list
			}

		else:
			return {}