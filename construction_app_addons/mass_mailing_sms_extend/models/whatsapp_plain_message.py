from odoo import fields,models,api,_
import logging
_logger = logging.getLogger(__name__)
import requests
from odoo.exceptions import UserError
import json
from odoo.http import request


class WhatsappPlainMessage(models.Model):
    _name='whatsapp.plain.message'
    _description = "Whatsapp Plain Message"

    name = fields.Char(string='Phone Number')
    date_initiated = fields.Datetime(string='Date', default=fields.Datetime.now)
    message_tag_content = fields.Char(string='Message')
    state = fields.Selection([('draft','Draft'),('sent','Sent'),('failed','Failed')],string='Status',default='draft')
    status_message = fields.Text(string='WhatsApp response')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    user = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, required=True)
    source_message = fields.Many2one('mailing.mailing', string='Message Source', required=True)

    # functions
    def action_confirm(self):
        self.write({'state': 'sent'})

    def action_draft(self):
        self.write({'state': 'draft'})
    # current company
    def get_current_company_value(self):

        cookies_cids = [int(r) for r in request.httprequest.cookies.get('cids').split(",")] \
            if request.httprequest.cookies.get('cids') \
            else [request.env.user.company_id.id]

        for company_id in cookies_cids:
            if company_id not in self.env.user.company_ids.ids:
                cookies_cids.remove(company_id)
        if not cookies_cids:
            cookies_cids = [self.env.company.id]
        if len(cookies_cids) == 1:
            cookies_cids.append(0)
        return cookies_cids
    def send_message(self, company_id,phone_no, text):
        # Chat api set up
        chatapi_settings = self.env['chat.api.setup'].search([('chatapi_state', '=', True),('company_id','=',company_id.id)], limit=1)
        if not chatapi_settings:
            raise UserError(_('Please add chat api settings! Cannot send message without chat api set up complete.'))

        data = {"chatID": chatapi_settings.name,
                "phone": phone_no,
                "body": text}
        # print("Send Message {} ".format(data))
        answer = self.send_requests('sendMessage', data)
        # #try to send a file for each request
        # file_data = {
        #     "chatID": chatID,
        #      "phone": phone_number[0],
        #      "body":  "https://upload.wikimedia.org/wikipedia/ru/3/33/NatureCover2001.jpg",
        #      "filename": "NatureCover2001.jpg",
        #      "caption": "Fonscom Real Estate Test"
        # }
        # send_file = send_requests('sendFile',file_data)

        return answer

    """
    function to send requests
    """

    def send_requests(self, method, data):
        ##
        # Chat api set up
        chatapi_settings = self.env['chat.api.setup'].search([('chatapi_state', '=', True)], limit=1)
        if not chatapi_settings:
            raise UserError(_('Please add chat api settings! Cannot send message without chat api set up complete.'))

        # self.dict_messages = json['messages']
        APIUrl = chatapi_settings.instance_url
        token = chatapi_settings.chatapi_access_token
        ####
        url = f"{APIUrl}{method}?token={token}"
        # url = "{}{}?token={}".format({self.APIUrl,method,self.token})
        _logger.info("URL >>>>>>>> ")
        _logger.info(url)
        headers = {'Content-type': 'application/json'}
        # print('Data to send {} '.format(data))
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        _logger.info("Debug::: Chat API Stats ")
        _logger.info(answer)
        return answer.json()
    # process message and send it then mark as sent. this is to avoid anti-spam system
    def whatsapp_plain_processing(self):
        if self.env.user.id == 1:
            self.odoo_bot_whatsapp_plain_processing()
        else:
            # incase a user is logged in and clicks process
            try:
                current_company = self.get_current_company_value()
                domain = [('state', '=', 'draft'), ('company_id', 'in', current_company)]
            except Exception as e:
                _logger.error("An error occured in whatsapp_plain_processing(): {0}".format(e))
                current_company = self.env.company.id
                domain = [('state', '=', 'draft'), ('company_id', '=', current_company)]
            # now check if the user logged in is OdooBot


            browse_messages = self.env['whatsapp.plain.message'].search(domain, limit=10)
            _logger.info("Debug::: Sending simple messages...")
            _logger.info(browse_messages)
            chatapi_settings = self.env['chat.api.setup'].search([('chatapi_state', '=', True),('company_id','=',current_company)], limit=1)
            if not chatapi_settings:
                raise UserError(_('Please add chat api settings! Cannot send message without chat api set up complete.'))
            for item in browse_messages:
                send_plain = self.env['whatsapp.plain.message'].send_message(current_company,item.name, item.message_tag_content)
                _logger.info("Debug::: WhatsApp response")
                if send_plain.get('sent'):
                    # change the status
                    item.state = 'sent'
                    item.status_message = send_plain.get('message') + " : " + send_plain.get('description')
                    item.status_message_technical = send_plain
                else:
                    item.state = 'failed'
                    item.status_message = send_plain.get('message') + " : " + send_plain.get('description')
                    item.status_message_technical = send_plain
                ####
                browse_source = self.env['mailing.mailing'].search([('id', '=', item.source_message.id)])
                if browse_source:
                    # mark the message as sent to avoid creation
                    browse_source.write({'redis_sent': True})
    # odoo bot processing messages
    def odoo_bot_whatsapp_plain_processing(self):
        messages = self.env['whatsapp.plain.message'].search([('state', '=', 'draft')], limit=10)
        for item in messages:
            send_plain = self.env['whatsapp.plain.message'].send_message(item.company_id,item.name, item.message_tag_content)
            _logger.info("Debug::: WhatsApp response")
            if send_plain.get('sent'):
                # change the status
                item.state = 'sent'
                item.status_message = send_plain.get('message') + " : " + send_plain.get('description')
                item.status_message_technical = send_plain
            else:
                item.state = 'failed'
                item.status_message = "API returned an Error"
                item.status_message_technical = send_plain
            ####
            browse_source = self.env['mailing.mailing'].search([('id', '=', item.source_message.id)])
            if browse_source:
                # mark the message as sent to avoid creation
                browse_source.write({'redis_sent': True})
