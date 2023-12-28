from odoo import fields,models,api,_
import logging
_logger = logging.getLogger(__name__)
import requests
from odoo.exceptions import UserError
import json
from odoo.http import request

class WhatsappCustomerReply(models.Model):
    _name='whatsapp.customer.reply'
    _description = "Customer Reply"

    name = fields.Char(string='Phone Number')
    sender_name = fields.Char(string='Profile Name')
    date_initiated = fields.Datetime(string='Date', default=fields.Datetime.now)
    message = fields.Char(string='Message Tag Content')
    chat_name = fields.Char(string='Chat Name')
    instance_id = fields.Char(string='Instance Name')
    forwarded_message = fields.Boolean(string='Is Forwarded Message',default=False)
    company_id = fields.Many2one('res.company', 'Company', required=False)
