from odoo import models,fields,_,api
from odoo.exceptions import UserError
import datetime
import requests
import logging
import json
_logger = logging.getLogger(__name__)
class mpesa_paybill_payments(models.Model):
    _name = 'failed.paybill.payments'
    _description='Record mpesa entries that have failed to process'

    # Transactions details
    name = fields.Char(string='Date')
    transaction = fields.Text(string='Transaction Details')

    status = fields.Selection([('draft','Failed'),('push','Re-Pushed'),('cancel','Cancelled')],
                              string='Status',default='draft')


    # we processed these records and send it to the endpoint that accepts transtion for processing
    def process_failed_transactions(self):
        # we execute one transaction at a time
        #transaction_details = self.search([('status','=','draft')],limit=1)
        _logger.info("Debug::: Transaction JSON to Resend")
        # endpoint to push to
        re_push_endpoint = 'https://apihalal.growdeskconsulting.com/amkatek/halal/api/v1.0/repush/confirmation/bills'
        #_logger.info(transaction_details[0].get('transaction'))

        for item in self.env['failed.paybill.payments'].search([('status','=','draft')]):
            message_structure = item.transaction
            try:
               _logger.info("CronTask TEST >>>>>>")
               #_logger.info(message_structure)
               #json_object = json.loads(message_structure)
               #_logger.info(json_object)
               res = requests.post(re_push_endpoint, json=message_structure)
               _logger.info('Server response {0}'.format(res))
               _logger.info("Sent >>>> ")
               item.write({'status': 'push'})
            except Exception as e:
                _logger.info('There was an exception pushing paybill details')
                _logger.info(e)
