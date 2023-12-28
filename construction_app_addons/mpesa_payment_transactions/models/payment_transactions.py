from odoo import models,fields,_

class MpesaPaymentTrasanctions(models.Model):
    _name = 'mpesa.payment.transaction'
    _description = 'MPESA Payment Transactions'

    name = fields.Char(string='Subscriber Mobile No')
    account_reference = fields.Char(string='Account Reference')
    merchant_request_id = fields.Char(string='Merchant Request ID')
    checkout_request_id = fields.Char(string='CheckOut Request ID')
    stk_push_status = fields.Selection([('0','Success'),('1','Failed')],string='STK Push Status')
    stk_push_note = fields.Text(string='STK-Push Note')
    payment_status = fields.Selection([('0','Success'),('1','Pending'),('1032','Cancelled'),('2001','Invalid Login')],
                                      string='Payment Status',default='1')
    payment_status_note = fields.Text(string='Payment Status Note')
    amount = fields.Float(string='Amount Paid')