# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class LoyaltyPointWizard(models.TransientModel):
	_name = 'loyalty.point.redeem.wizard'
	
	product_id = fields.Many2one('product.product', 'Select Gift Product', domain="[('is_gift_product', '=', True)]", required=True)
	partner_id = fields.Many2one('res.partner', 'Customer', readonly=False)
	loyalty_points = fields.Integer(string='Loyalty Points Have', compute='onc_gift_product',store=True)
	after_redeem = fields.Integer(string='Loyalty Points Left', compute='onc_gift_product',store=True)
	loyalty_used = fields.Integer(string='Loyalty Points Used', compute='onc_gift_product',store=True)
	loyalty_history_id = fields.Many2one('loyalty.history',string="Loyalty history")
	extra_note = fields.Text(string="Note")
	is_redeemed = fields.Boolean('Is Redeemed')

	@api.depends('product_id','partner_id')
	def onc_gift_product(self):
		self.loyalty_points = self.partner_id.loyalty_points
		if self.loyalty_points <  self.product_id.num_of_points : 
			raise ValidationError(_('You can not redeem more points than you have.'))
		else:
			diff = self.loyalty_points - self.product_id.num_of_points
			self.after_redeem = diff
			self.loyalty_used = self.product_id.num_of_points
	
	def button_redeem_points(self):
		point_cal = int(self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.point_cal'))
		if point_cal < 1:
			raise UserError(_("Please configure redeem point amount under Loyalty Management->configuration->settings"))
		else:
			vals = {
				# 'payment_id':self.id,
				# 'payment_amount' : self.product_id.,
				'partner_id': self.partner_id.id,
				'date' : datetime.now().date() ,
				'points': self.product_id.num_of_points,
				'transaction_type' : 'send',
				'product_id' : self.product_id.id,
				'total_points': self.partner_id.loyalty_points - self.product_id.num_of_points,
				'extra_note': self.extra_note,
				'total_payment_amount': 0.0,
			}
			if self.partner_id.last_yr_loyalty_points >= self.product_id.num_of_points :
				vals.update({
					'used_from_last': True,
				})
			loyalty_history = self.env['loyalty.history'].create(vals)
			self.write({
				'loyalty_history_id':loyalty_history.id,
				'is_redeemed': True
			})
			self.create_picking(loyalty_history)
			data = {'redeem':loyalty_history.id}
			return self.env.ref('bi_sale_loyalty.action_redeem_receipt').report_action([],data = data)
	#custom function to redeem points on sale orders success
	@api.model
	def redeem_points_on_sale_order(self,partner_id,points,product_id,total_points):
		partner = self.env['res.partner'].search([('id','=',partner_id)])
		vals = {
			# 'payment_id':self.id,
			# 'payment_amount' : self.product_id.,
			'partner_id': partner_id,
			'date': datetime.now().date(),
			'points': points,
			'transaction_type': 'send',
			'product_id': product_id,
			'total_points': total_points - points,
			'extra_note': 'Redeemed via mobile app',
			'total_payment_amount': 0.0,
		}
		if partner.last_yr_loyalty_points >= points:
			vals.update({
				'used_from_last': True,
			})
		loyalty_history = self.env['loyalty.history'].create(vals)
		self.write({
			'loyalty_history_id': loyalty_history.id,
			'is_redeemed': True
		})
		self.create_picking(loyalty_history)
		return True

	def create_picking(self,loyalty_history):
		stock_picking_obj = self.env['stock.picking']
			
		picking_type_id = self.env['stock.picking.type'].search([('code','=','outgoing'),
						('warehouse_id.company_id','=',self.env.user.company_id.id)])[0]

		vals= {
			'partner_id' : loyalty_history.partner_id.id,
			'location_id' : picking_type_id.default_location_src_id.id,
			'location_dest_id' : loyalty_history.partner_id.property_stock_customer.id,
			'origin' : loyalty_history.product_id.name,
			'scheduled_date' : datetime.now(),
			'picking_type_code' : 'outgoing',
			'picking_type_id' : picking_type_id.id,
		}
		stock_picking = stock_picking_obj.create(vals)
		loyalty_history.write({
			'delivery_order_id' : stock_picking.id,
			})

		product_vals = {
			'name' : loyalty_history.product_id.name,
			'product_id' : loyalty_history.product_id.id,
			'product_uom_qty' : 1.0,
			'product_uom' : loyalty_history.product_id.uom_id.id,
			'picking_id' : stock_picking.id,
			'location_id' : stock_picking.location_id.id,
			'location_dest_id' : stock_picking.location_dest_id.id,
		}
		stock_move = self.env['stock.move'].create(product_vals)
		immediate_transfer = self.env['stock.immediate.transfer'].create({'pick_ids':[(6,0,[stock_picking.id])]})
		stock_picking.action_assign()
		immediate_transfer.process()



class RedeemReceiptReport(models.AbstractModel):

	_name = 'report.bi_sale_loyalty.report_redeem_receipt'
	_description = 'Redeem Receipt Report'

	@api.model
	def get_sale_details(self,lhistory=False):
		return {
			'currency_precision': 2,
			'company_name': self.env.user.company_id.name,
			'points' : lhistory.points,
			'partner_id': lhistory.partner_id,
			'product_id' : lhistory.product_id,
			'total_points': lhistory.partner_id.loyalty_points,
			'extra_note': lhistory.extra_note,
		}

	def _get_report_values(self, docids, data=None):
		data = dict(data or {})
		lhistory = self.env['loyalty.history'].browse(data['redeem'])
		data.update(self.get_sale_details(lhistory))
		return data
