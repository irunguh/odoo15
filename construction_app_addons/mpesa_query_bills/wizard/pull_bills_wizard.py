from odoo import api, fields, models,_
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
import requests
import json
_logger = logging.getLogger(__name__)
class PullMpesaWizard(models.Model):
    _name = 'pullmpesa.bills.wizard'
    _description='Pull Mpesa bill wizard'

    transaction_no = fields.Char(string='Transaction Code',required=True,help='Transaction code from mpesa message. '
                                                                 'This will be used to pull details from mpesa')
    customer_account = fields.Char(string='Customer Account No',required=True,
                                   help='The account number that this payment was done for.'
                                                                     'This is used by the ERP during reconcilation')
    #Pull bills from mpesa
    def pull_mpesa_bills_from_mpesa(self):
        # we send a post to our endpoint that receives mpesa notification and inserts data
        # TODO Add module for these settings
        # mpesa authentication settings
        # CommandID = "TransactionStatusQuery",
        # PartyA =  "4077777",
        # IdentifierType =  "4",
        # Remarks = "Remarks",
        # Initiator = "mohamed777",
        # SecurityCredential = "MT91EX2a9SrchTqcHDrhcEKPi/e0CZYY2UB+msYSgI/zPerCYGRXu5VjuRl5IUTDBIVdH8ODFUjPGVROfIplDzAIyBiall5f12pxzNjdJo1OC8JzJmtXKh9hazn1iAa8GAAgrhiswVYGmVpsTxV2oO3s49KG1Nkwu/W8Nd/iHwgyC+Se9eFlbVVDXzy6DsAuGRSSLm+v6I6vglk/j08OJQckXnvzriCprx5gB4b/3fxbmhbS4jtD95S3d2DzbtS1oqBwVg2wLVDfVZugx51UBwSls7RRU3Ntv9bDItFotFpNxd6rhZ5h8VeWQNpYej1Fb6U8dIOdJP4jLFw23GFHHg==",
        # QueueTimeOutURL = "https://apihalal.growdeskconsulting.com/amkatek/halal/api/v1.0/mpesa/transactiontimeout",
        # ResultURL = "https://apihalal.growdeskconsulting.com/amkatek/halal/api/v1.0/mpesa/transactionsresults",
        # TransactionID = self.transaction_no
        ### query
        query_bill_endpoint = 'https://apihalal.growdeskconsulting.com/amkatek/halal/api/v1.0/mpesa/checktransactionstatus'
        message_structure = {
            "CommandID": "TransactionStatusQuery",
            "PartyA": "4077777",
            "IdentifierType": "4",
            "Remarks": "Remarks",
            "Initiator": "mohamed777",
            "SecurityCredential": "MT91EX2a9SrchTqcHDrhcEKPi/e0CZYY2UB+msYSgI/zPerCYGRXu5VjuRl5IUTDBIVdH8ODFUjPGVROfIplDzAIyBiall5f12pxzNjdJo1OC8JzJmtXKh9hazn1iAa8GAAgrhiswVYGmVpsTxV2oO3s49KG1Nkwu/W8Nd/iHwgyC+Se9eFlbVVDXzy6DsAuGRSSLm+v6I6vglk/j08OJQckXnvzriCprx5gB4b/3fxbmhbS4jtD95S3d2DzbtS1oqBwVg2wLVDfVZugx51UBwSls7RRU3Ntv9bDItFotFpNxd6rhZ5h8VeWQNpYej1Fb6U8dIOdJP4jLFw23GFHHg==",
            "QueueTimeOutURL": "https://apihalal.growdeskconsulting.com/amkatek/halal/api/v1.0/mpesa/transactiontimeout",
            "ResultURL": "https://apihalal.growdeskconsulting.com/amkatek/halal/api/v1.0/mpesa/transactionsresults" ,
            "TransactionID": self.transaction_no
        }
        # send
        res = requests.post(query_bill_endpoint, json=message_structure)
        json_data = json.loads(res.text)
        _logger.info(json_data)
        if json_data.get('message') == 'Success':
           # search for the bill details - if it exists and is processed return error
           search_bill = self.env['mpesa.paybill.payments'].search([('mpesa_transaction_no','=',self.transaction_no),('status','!=','invalid')])
           if search_bill:
               raise UserError(_('Sorry this transaction already exists and has been processed!'))
           # process
           self.env['missing.paybill.payments'].create({
               'name': self.transaction_no,
               'account_no': self.customer_account
           })
        else:
            raise UserError(_('Could not query bill {0} at this time. Please try again later!'.format(self.transaction_no)))

        return True