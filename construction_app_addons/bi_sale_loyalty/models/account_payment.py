# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)
import requests
class AccountPaymentInherit(models.Model):
	_inherit = "account.payment"

	loyalty_used_from_last = fields.Boolean(string='Used from last')

	# get points set for a product using the pricelist
	def get_points_from_pricelist(self,pricelist_id,product_id):
	  #print("Debug::::: Search using {0} {1}".format(pricelist_id,product_id))
	  _logger.info("Debug:::: get_points_from_pricelist{0} ::: product_id {1} ".format(pricelist_id,product_id))
	  # using pricelist id, and product id get a specific product set points
	  set_points = self.env['product.pricelist.item'].search([('pricelist_id','=',pricelist_id),('product_tmpl_id','=',product_id)],limit=1)

	  return int(set_points.ice_points_to_accrue)
    #send whatsapp notifications
	def save_payment_receipt(self, partner_phone_no, partner_name, invoice_no, payment_id):
		#check if payment exists before saving
		payment_exists = self.env['payment.receipt.monitor'].search([('payment_id','=',payment_id)])
		if payment_exists:
			_logger.info("Debug::: Payment Receipt with ID {0} exists. Do not create a new entry!".format(payment_exists.payment_id))
		else:
			payment_obj = self.env['payment.receipt.monitor'].create({
				'name': partner_name,
				'phone': partner_phone_no,
				'invoice_no': invoice_no,
				'payment_id': payment_id
			})
		return True
	#Points notification
	def send_points_accrue_notification(self,customer_name,phone_no,points,amount_paid,invoice_no):
		##
		if phone_no:
			message = 'Dear {0}, You have earned {1} points from payment of KES {2} for Invoice {3}. Thank you.'.format(customer_name,points,amount_paid,invoice_no)
			whatsapp_url = 'https://apihalal.growdeskconsulting.com/amkatek/halal/api/v1.0/chatapi/sendnotification'
			message_structure = {
				'phone': phone_no,
				'message': message
			}
			res = requests.post(whatsapp_url, json=message_structure)

    # ice points - retur value as configured
	@api.model
	def ice_points_value_conf(self):
		return  int(self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.point_redeem_value'))

	def action_draft(self):
		_logger.info("Debug:::: Action Draft in Account Payment")
		# when you draft this, we will have to cancel all loyalty points associated with this payment and recreate after reconciliation
		loyaly_points_ref = self.env['loyalty.history'].search([('payment_id','=',self.name)])
		if loyaly_points_ref:
			# update to cancel
		    loyaly_points_ref.write({'transaction_type': 'cancel','extra_note': 'Payment was Rest to Draft.This means we remove the points.'})
		res = super(AccountPaymentInherit, self).action_draft()

# odoo 13 provides this hook to use when an invoice payment status change to paid
class AccountMoveHook(models.Model):
	_inherit = 'account.move'
	# function to get points
	def get_points_from_pricelist(self,pricelist_id,product_id):
	  #print("Debug::::: Search using {0} {1}".format(pricelist_id,product_id))
	  _logger.info("Debug:::: get_points_from_pricelist{0} ::: product_id {1} ".format(pricelist_id,product_id))
	  # using pricelist id, and product id get a specific product set points
	  set_points = self.env['product.pricelist.item'].search([('pricelist_id','=',pricelist_id),('product_tmpl_id','=',product_id)],limit=1)

	  return int(set_points.ice_points_to_accrue)
    # odoos 13 hook
	def action_invoice_paid(self):
		''' Hook to be overrided called when the invoice moves to the paid state. '''
		_logger.info("Hook to be overrided called when the invoice moves to the paid state")

		#_logger.info(self.name)
		point_cal = int(self.env['ir.config_parameter'].sudo().get_param('bi_sale_loyalty.point_cal'))

		loyalty_history = False
		if point_cal > 0:
			# new_loyalty = int(self.amount / point_cal)
			# Amkatek patch
			# SELECT * FROM account_move_line WHERE move_id = 13 and parent_state = 'posted' and product_id > 0
			# First select the invoice lines affected by this purchase
			######### invoice
			invoice = self
			# customer pricelist
			customer_pricelist_id = invoice.partner_id.property_product_pricelist.id
			########## invoice lines
			# lets iterate - Assume a user is doing multiple reconcilation, each invoice is paid and a client will earn points
			for inv in invoice:
				read_invoice_lines = self.env['account.move.line'].search([('move_id', '=', inv.id),
																		   ('parent_state', '=', 'posted'),
																		   ('product_id', '!=', False)])
				custom_points = 0
				# loop
				for lines in read_invoice_lines:
					# this is an invoice for buying ice points
					if lines.product_id.is_for_ice_points == True:
						# 1 point = 2
						total_paid = (lines.quantity * lines.product_id.list_price)
						results = (total_paid * point_cal)
						# custom_points += results/lines.product_id.list_price
						custom_points += lines.quantity
					else:  # Award as set per price
						custom_points += self.get_points_from_pricelist(customer_pricelist_id,
																		lines.product_id.id) * lines.quantity

				# this is a summation of points set on a product and quntity purchased
				new_loyalty = int(custom_points)
				# print("************** POINTS ********************")
				# print(new_loyalty)
				########## end custom
				if new_loyalty > 0:
					# if this an invoice we sent to customer not supplier invoice
					if inv.type == 'out_invoice':
						# get payment reference linked to this invoice
						domain = [('communication','=',inv.name)]
						payment_ref_obj = self.env['account.payment'].search(domain)
						_logger.info("XXXXXXXXXXXXXXXXXXXXXXXXX DEBUG XXXXXXXXXXXXXXXXXXXXXXXX")
						_logger.info(payment_ref_obj)
						_logger.info(domain)
						# multiple invoices reconciled manually
						# use extra note field to show invoice
						extra_note = ''
						if not payment_ref_obj:
							# try to search for invoices with this as payment reference
							#payment_ref_obj = self.env['account.payment'].search([('move_name','in',self.ids)])
							# TODO - figure out how the relationship on reconcilation payment is created
							# TODO - we have a situation where a user manually reconciles check payments which can link to multiple invoices and searching to link and show payment reference in loyalty points is impossible
							extra_note = inv.name # we just note the connected invoice
						# check invoice is paid
						# we only assign points if its fully paid
						if inv.invoice_payment_state == 'paid':
							# we must check and make sure we dont have a payment, if we have multiple payments
							# we assume that this invoice was paid halfway and earned its points so do not earn points just mark as paid
							if len(payment_ref_obj) > 1 :
								_logger.info("No points since it had earned points...")
							else: # earn points
								vals = {
									'transaction_type': 'receive',
									'total_payment_amount': inv.partner_id.total_amount + inv.amount_total,
									# 'total_points': inv.partner_id.loyalty_points + new_loyalty,
									'payment_id': payment_ref_obj.id,
									'partner_id': inv.partner_id.id,
									'date': datetime.now().date(),
									'points': new_loyalty,
									'payment_amount': inv.amount_total,
									'extra_note': extra_note
								}
								_logger.info("Debug::::::::Earn points...{0}".format(vals))
								# _logger.info("XXXXXXXXXXX We have disabled notifications for now !!!!")
								loyalty_history = self.env['loyalty.history'].create(vals)

								payment_ref_obj.save_payment_receipt(inv.partner_id.mobile, inv.partner_id.name,
																	 payment_ref_obj.communication,
														  inv.id)
								# # send whatsapp points notification message for complete invoice payments
								# payment_ref_obj.send_points_accrue_notification(inv.partner_id.name,
								# 									 inv.partner_id.mobile, vals.get("points"),
								# 									 inv.amount_total, inv.name)
						else:
							_logger.info("No points earned for invoice {0}".format(inv.name))
							# remember to send a receipt for all payments
							payment_ref_obj.save_payment_receipt(inv.partner_id.mobile, inv.partner_id.name,
																 payment_ref_obj.communication,
													  inv.id)
