# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, datetime

class customer_points_report_wiz(models.TransientModel):

	_name='customer.points.report.wizard'

	start_dt = fields.Date('Start Date', required = True)
	end_dt = fields.Date('End Date', required = True)
	customer_ids = fields.Many2many('res.partner',string="Customers")
	status = fields.Selection([('all', 'All'),('receive', 'Receive'), ('send', 'Send'),('cancel','Cancel')], string='Status',default='all')
	product_ids = fields.Many2many('product.product',string="Products", domain="[('is_gift_product', '=', True)]")
	
	def customer_points_generate_report(self):
		return self.env.ref('bi_sale_loyalty.action_customer_points_report').report_action(self)


class HistoryReport(models.AbstractModel):

	_name='report.bi_sale_loyalty.report_customer_points_history'
	
	def _get_report_values(self, docids, data=None):
		customer_rec = self.env['customer.points.report.wizard'].browse(docids)
		main_data_dict = {} 
		customer_data = []
		product_filter = []
		partner_filter = []

		domain = [('date','>=',customer_rec.start_dt),('date','<=',customer_rec.end_dt)]

		if customer_rec.status and customer_rec.status != 'all':
			domain += [('transaction_type','=',customer_rec.status)]

		if customer_rec.customer_ids : 
			domain += [('partner_id','in',customer_rec.customer_ids.ids)]
			for i in customer_rec.customer_ids:
				partner_filter.append(i.name)


		if customer_rec.product_ids:
			domain += [('product_id','in',customer_rec.product_ids.ids)]
			for i in customer_rec.product_ids:
				product_filter.append(i.name)

		
		
		history_summary = self.env['loyalty.history'].search(domain).ids

		if history_summary:
			if customer_rec.status == 'all': 
				self.env.cr.execute("""
					SELECT partner.id ,partner.name ,partner.loyalty_points total
					FROM loyalty_history AS lh,
						 res_partner AS partner
					WHERE  lh.id IN %s 
						AND lh.points > 0
						AND partner.id = lh.partner_id

					GROUP BY partner.id 
					""", (tuple(history_summary),))
				customer_data = self.env.cr.dictfetchall()
			else:
				self.env.cr.execute("""
					SELECT partner.id ,partner.name , sum(lh.points) total
					FROM loyalty_history AS lh,
						 res_partner AS partner
					WHERE  lh.id IN %s 
						AND lh.points > 0
						AND partner.id = lh.partner_id

					GROUP BY partner.id 
					""", (tuple(history_summary),))
				customer_data = self.env.cr.dictfetchall()
		else:
			customer_data = []

		parnters_list = ', '.join(map(str,partner_filter) )
		products_list = ', '.join(map(str,product_filter) )

		return {
			'status': customer_rec.status,
			'products': customer_rec.product_ids,
			'customers': customer_rec.customer_ids,
			'customer_data' : customer_data,
			'start_dt' : customer_rec.start_dt,
			'end_dt' : customer_rec.end_dt,
			'partner_filter' : parnters_list, 
			'product_filter' : products_list
		}
	