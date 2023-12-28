from odoo import models,fields,_,api
from odoo.exceptions import UserError
import datetime
import re


import logging
_logger = logging.getLogger(__name__)
class mpesa_paybill_payments(models.Model):
    _name = 'mpesa.paybill.payments'
    _description='Record mpesa entries from paybill payments'

    #function to register paybill payments
    def register_paybill_payments(self):
        # we create entries and register payments for this customer and update the transaction on table with paybill entries
        # model to register payments in
        payment_register = self.env['account.payment']
        partner_invoices = self.env['account.move']
        # pending payments
        pending_payments = self.env['mpesa.paybill.payments'].search([('status','=','draft')],limit=100,order="id asc")
        #_logger.info("Debug:: Pending Payments .....")
        #_logger.info(pending_payments)
        #new payments
        for item in pending_payments:
            # remove any spaces
            customer_phone = item.account_no.lstrip(' ')
            reformat_phone = None
            # remove the first zero
            if len(customer_phone) > 13 and len(customer_phone) < 10:
                _logger('Paybill Error::: Phone number {0} is Invalid'.format(customer_phone))
            # starts with 254
            if customer_phone.startswith('254'):
                new_phone = '+' + customer_phone
                reformat_phone = customer_phone

            # starts with zero
            elif customer_phone.startswith('0'):
                new_phone = customer_phone.lstrip('0')
                new_phone = '+254' + new_phone
                reformat_phone = new_phone
            # start with 1
            elif customer_phone.startswith('1'):
                #new_phone = customer_phone.lstrip('0')
                new_phone = '+254' + new_phone
                reformat_phone = new_phone
            # starts with 1
            # starts with +
            elif customer_phone.startswith('+254'):
                reformat_phone = customer_phone
            # whatever
            else:
                reformat_phone = customer_phone
            #############################
            #_logger.info("Debug:: Correct phone number {0} ".format(reformat_phone))
            #_logger.info("Debug:: Correct phone number stringed {0} ".format(str(reformat_phone)))
            search_domain = [('mobile','=',reformat_phone)]
            #_logger.info("Debug:: Search domain is {0}".format(search_domain))
            customer_id = self.env['res.partner'].search(search_domain,limit=1)
            #_logger.info("Debug:: Searching Customer Ids {0} ".format(customer_id))
            # because of the new phone numbers without zeros - just try as is
            # if not customer_id:
            #     reformat_phone = "+254" + customer_phone
            #     customer_id = self.env['res.partner'].search([('mobile', '=', reformat_phone)], limit=1)
            #print(item.account_no.lstrip(' '))
            #_logger.info('Register Payment for {0} and customer phone is {1}'.format(customer_id.id,reformat_phone))
            # we only process if we have found a customer
            if customer_id.id:
                ## date of payment
                custom_datetime = item.payment_date
                convert = datetime.datetime.strptime(custom_datetime, '%Y-%m-%d %H:%M:%S')
                #print("Register payments vars {0}".format(vars))
                # we need to mark old invoice as paid and reduce customer debt - we search by oldest
                search_invoice_obj = partner_invoices.search([('partner_id','=',customer_id.id),('amount_residual','>',0),('state','=','posted')],order="id asc",limit=1)
                # Get invoice amount to be paid
                invoice_debt_to_pay = search_invoice_obj.amount_residual
                #_logger.info("Paybill payments Reconcilation Action")
                #_logger.info(" Payment Amount from Paybill {0} : Invoice to pay {1}".format(item.name,search_invoice_obj.name))
                #now check amount paid
                if float(item.amount) < invoice_debt_to_pay or float(item.amount) == invoice_debt_to_pay:
                    _logger.info('Debug Register Paybill Payments:: Step 1. Amount paid is less or clears the pedning debt')
                    # we just pay this invoice and update the record from mpesa to done and no credit for another invoice
                    create_payments = search_invoice_obj.custom_resolve_payment(float(item.amount),convert,'mpesa',item.mpesa_transaction_no)
                    if create_payments:
                        update = item.write({'status': 'done'})
                        try:
                            # Save message to send to our customer
                            _logger.info("Debug:::: Register payment >>>>>>>>> Save message to send to our customer")
                            message = 'Dear {0}, KES {1} Payment has been posted to your account  {2} . Balance due KES {3}. For enquiries call 0756111111'.format(
                                customer_id.name, float(item.amount), customer_id.mobile, "{0}")
                            payment_obj = self.env['custom.sms.notification'].create({
                                'phone': customer_id.mobile,
                                'message': message,
                                'status': 'draft',
                                'is_payment_sms': True,
                                'is_posted_invoice_sms': False
                            })
                            return True
                        except Exception as e:
                            _logger.error('Error: register_paybill_payments > Please note sms could not save!')
                            _logger.info(e)
                else:
                    _logger.info('Debug:: Step 2. Amount paid is higher and there is an outstanding credit.')
                    # Only process if we have an invoice
                    if search_invoice_obj.id:
                        # here is the challenge, the customer has paid more than what is set for this invoice
                        # we have to mark invoice as paid and the balance we push it to the next available invoce
                        # lets pay what is required and balance move it to credit column for next invoice to reconcile
                        #_logger.info("Multiple Invoices payment actions")
                        create_payments2 = search_invoice_obj.custom_resolve_payment(invoice_debt_to_pay, convert,'mpesa',item.mpesa_transaction_no)
                        available_credit = float(item.amount) - invoice_debt_to_pay
                        # print("Debug::: invoice_debt_to_pay {0}".format(invoice_debt_to_pay))
                        # print("Debug::: item.amount {0}".format(item.amount))
                        # print("Debug::: available_credit {0}".format(available_credit))
                        if create_payments2:
                            #_logger.info("Paid Invoice {0} : moved the balance for reconcilation ".format(search_invoice_obj.name))
                            #print('Debug:: Before updating balance to reconcile')
                            update1 = item.write({'status': 'reconcile'} )
                            update2 = item.write({'balance_to_reconcile': available_credit})
                            #print('Debug:: After updating balance to reconcile {0} >>> {1}'.format(update1,update2))
                            search_invoice_obj.write(
                                {'to_notify': False})  # helps us to avoid sending notification if its for reconcilation
                            #### Over payment notification
                            try:
                                # Save message to send to our customer
                                _logger.info(
                                    "Debug:::: Register Over payment >>>>>>>>> Save message to send to our customer")
                                message = 'Dear {0}, KES {1} Payment has been posted to your account  {2} . Balance due KES {3}. For enquiries call 0756111111'.format(
                                    customer_id.name, float(item.amount), customer_id.mobile, "{0}")
                                payment_obj = self.env['custom.sms.notification'].create({
                                    'phone': customer_id.mobile,
                                    'message': message,
                                    'status': 'draft',
                                    'is_payment_sms': True,
                                    'is_posted_invoice_sms': False
                                })
                                return True
                            except Exception as e:
                                _logger.error('Error: Registering Over Payment Message. > Please note sms could not save!')
                                _logger.info(e)
            #else:

    def reconcile_invoice_payments(self):
        _logger.info('Debug::: Start Auto Reconcilation process....')
        partner_invoices = self.env['account.move']
        # TODO payments to reconcile - Find a better method to handle this important client request
        for item in self.env['mpesa.paybill.payments'].search([('status','=','reconcile')]):
            customer_phone = item.account_no
            customer_phone = re.sub(r"\s+", "", customer_phone, flags=re.UNICODE)
            reformat_phone = None
            # phone number formatting
            # starts with 254
            if customer_phone.startswith('254'):
                new_phone = '+' + customer_phone
                reformat_phone = customer_phone

            # starts with zero
            elif customer_phone.startswith('0'):
                new_phone = customer_phone.lstrip('0')
                new_phone = '+254' + new_phone
                reformat_phone = new_phone
            # start with 1
            elif customer_phone.startswith('1'):
                # new_phone = customer_phone.lstrip('0')
                new_phone = '+254' + new_phone
                reformat_phone = new_phone
            # starts with 1
            # starts with +
            elif customer_phone.startswith('+254'):
                reformat_phone = customer_phone
            # whatever
            else:
                reformat_phone = customer_phone
            # search
            customer_id = self.env['res.partner'].search([('mobile','=',reformat_phone)],limit=1)
            ## date of payment
            custom_datetime = item.payment_date
            convert = datetime.datetime.strptime(custom_datetime, '%Y-%m-%d %H:%M:%S')
            #print("Register payments vars {0}".format(vars))
            # we need to mark old invoice as paid and reduce customer debt - we search by oldest
            search_invoice_obj = partner_invoices.search([('partner_id','=',customer_id.id),('amount_residual','>',0),('state','=','posted')],order="id asc",limit=1)
            # Get invoice amount to be paid
            invoice_debt_to_pay = search_invoice_obj.amount_residual
            # now check amount available as credit to reconcile with
            available_credit = 0
            if float(item.balance_to_reconcile) < invoice_debt_to_pay or float(item.balance_to_reconcile) == invoice_debt_to_pay:

                search_invoice_obj.write(
                    {'to_notify': False})  # helps us to avoid sending notification if its for reconcilation
                # we just pay this invoice from credit available
                create_payments = search_invoice_obj.custom_resolve_payment(float(item.balance_to_reconcile), convert,'mpesa',item.mpesa_transaction_no)
                if create_payments:
                    available_credit = item.balance_to_reconcile - invoice_debt_to_pay
                    if available_credit > 0:
                        _logger.info("Debug>>>> !!!!!!!!!! Some balances available {0}".format(available_credit))
                        update = item.write({'status': 'reconcile', 'balance_to_reconcile': available_credit})
                    else:
                        #no more credit to use
                        _logger.info("Debug>>>>> no more credit to use")
                        try:
                            # Save message to send to our customer
                            message = 'Dear {0}, KES {1} Credit has been used to clear bill {2}. New Balance due is KES {3}. For enquiries call 0756111111'.format(
                                customer_id.name, float(item.balance_to_reconcile), search_invoice_obj.name, "{0}")
                            payment_obj = self.env['custom.sms.notification'].create({
                                'phone': customer_id.mobile,
                                'message': message,
                                'status': 'draft',
                                'is_payment_sms': True,
                                'is_posted_invoice_sms': False
                            })
                        except Exception as e:
                            _logger.error('Error: reconcile_invoice_payments > Please note sms could not save!')
                            _logger.info(e)
                        update = item.write({'status': 'done', 'balance_to_reconcile': 0})
            else:
                search_invoice_obj.write(
                    {'to_notify': False})  # helps us to avoid sending notification if its for reconcilation
                # we pay and record remaining credit
                _logger.info("Debug>>> helps us to avoid sending notification if its for reconcilation")
                if invoice_debt_to_pay != 0.0:
                    create_payments2 = search_invoice_obj.custom_resolve_payment(invoice_debt_to_pay, convert,'mpesa',item.mpesa_transaction_no)
                    available_credit = float(item.balance_to_reconcile) - invoice_debt_to_pay
                    _logger.info("Debug>>> !!!!!!!!!!!!!!!!!!!!!!!!! available_credit {0}".format(available_credit))
                    if create_payments2:
                        update = item.write({'status': 'reconcile', 'balance_to_reconcile': available_credit})
                else:
                    _logger.info("Debug>>> !!!!!!!!!!!!!!!! No Invoice to reconcile with amount {0}".format(item.balance_to_reconcile))

    name = fields.Char(string='Customer')
    transaction_type = fields.Char(string='Transaction Type')
    mpesa_transaction_no = fields.Char(string='Transaction No')
    payment_date = fields.Char(string='Payment Date')
    phone_no = fields.Char(string='Paying Phone Number(MSISDN)')
    account_no = fields.Char(string='Account No/BillRefNumber/Customer Phone')
    amount = fields.Char(string='Amount Paid')
    status = fields.Selection([('draft','Draft'),('reconcile','To Reconcile'),('done','Done'),('invalid','Invalid')],
                              string='Status',default='draft')
    balance_to_reconcile = fields.Float(string='Balance to Reconcile',required=False,default=lambda self: self.amount)