from odoo import fields,models,api,_
import logging
_logger = logging.getLogger(__name__)
import requests
from odoo.exceptions import UserError
import json


class ChatAPISetup(models.Model):
    _name='chat.api.setup'
    _description="Chat API set up"

    name = fields.Char(string='Chat ID',help='Copy from Chat API dashboard')
    instance_url = fields.Char(string='Instance URL', help='Copy from Chat API dashboard')
    chatapi_access_token = fields.Char(string='Chat API Token', help='Copy from Chat API')
    chatapi_state = fields.Boolean(string='State of Instance',default=False)
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)

