from odoo import models,fields,_,api
from odoo.exceptions import UserError
import datetime
import requests
import logging
import json
_logger = logging.getLogger(__name__)
class mpesa_missing_paybill_payments(models.Model):
    _name = 'missing.paybill.payments'
    _description='Pull Mpesa bills using paybill'

    # Transactions details
    name = fields.Char(string='Transaction Code')
    transaction_type = fields.Text(string='Transaction Type',default='Pay Bill')
    customer = fields.Char(string='Customer')
    payment_date = fields.Char(string='Payment Date')
    payer_phone = fields.Char(string='Paid By')
    account_no = fields.Char(string='Account Number')
    amount = fields.Char(string='Amount Paid')

    status = fields.Selection([('draft','Draft'),('process','Processed'),('cancel','Cancelled')],
                              string='Status',default='draft',help='The system will run a cron task to update these items')


    # we processed these records and send it to the endpoint that accepts transtion for processing
    def process_missing_transactions(self):
        pulled_endpoint = 'https://apihalal.growdeskconsulting.com/amkatek/halal/api/v1.0/process/pulled/mpesa/bills'
        _logger.info("Debug::: process_missing_transactions() function")
        for item in self.search([('status','=','draft')]):
            if item.amount is not None:
                json_struct = {
                    'name': item.name,
                    'transaction_type': item.transaction_type,
                    'customer': item.customer,
                    'payment_date': item.payment_date,
                    'payer_phone': item.payer_phone,
                    'account_no': item.account_no,
                    'amount': item.amount
                }
                send_request = requests.post(pulled_endpoint,json=json_struct)
                item.write({'status': 'process'})