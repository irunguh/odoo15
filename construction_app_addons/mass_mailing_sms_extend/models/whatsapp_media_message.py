from odoo import fields,models,api,_
import logging
import pika
_logger = logging.getLogger(__name__)
import requests
from odoo.exceptions import UserError
import json
from odoo.http import request
# redis implementation for messaging
import redis
import os

class WhatsappMediaMessage(models.Model):
    _name='whatsapp.media.message'
    _description = "WhatsApp Media Message"

    name = fields.Char(string='Phone Number')
    date_initiated = fields.Datetime(string='Date',default=fields.Datetime.now)
    message_tag_content = fields.Char(string='Message Tag Content')
    category = fields.Char(string='Target Group')

    message_public_image_link = fields.Char(string='Message Image Link')
    state = fields.Selection([('tosend','ToSend'),('forcedsend','Forced Send'),
                              ('draft','Draft'),('sent','Sent'),('done','Done'),
                              ('failed','Failed')],string='Status',default='draft')
    status_message = fields.Text(string='WhatsApp response')
    status_message_technical = fields.Text(string='WhatsApp response Technical')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    user = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, required=True)
    source_message = fields.Many2one('mailing.mailing',string='Message Source', required=True)

    # functions
    def action_confirm(self):
        self.write({'state': 'sent'})
    def action_draft(self):
        self.write({'state': 'draft'})
    # current company
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
    # Sending Whatsapp messages
    """
    function to send file to a whatsApp number
    https://app.chat-api.com/docs#sendFile
    """

    def send_a_file(self, chatID, phone_number, image_link, file_name, caption_text):
        # try to send a file for each request
        file_data = {
            "chatID": chatID,
            "phone": phone_number,
            # "body": "https://upload.wikimedia.org/wikipedia/ru/3/33/NatureCover2001.jpg",
            "body": image_link,
            "filename": file_name,
            "caption": caption_text
        }
        _logger.info("Debug:::: Chat API Send File Data :::::: ")
        _logger.info(file_data)
        answer = self.send_requests('sendFile', file_data)
        _logger.info("debug:::: send_requests response in send_a_file {0}".format(answer))

        return answer

    # borrowed from whatsapp chat api function
    """
    function to send message back to ChatAPI
    """

    def send_message(self, company_id,phone_no, text):
        # Chat api set up
        chatapi_settings = self.env['chat.api.setup'].search([('chatapi_state', '=', True),('company_id','=',company_id)], limit=1)
        if not chatapi_settings:
            raise UserError(_('Please add chat api settings! Cannot send message without chat api set up complete.'))

        data = {"chatID": chatapi_settings.name,
                "phone": phone_no,
                "body": text}
        # print("Send Message {} ".format(data))
        _logger.info("Debug::::: Send Message ::::")
        _logger.info(data)
        answer = self.send_requests('sendMessage', data)
        _logger.info("debug:::: send_requests in send_message response {0}".format(answer))
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
        _logger.info("Debug>>>>> CHAT ID {0}".format(data.get("chatID")))
        # Chat api set up
        chatapi_settings = self.env['chat.api.setup'].search([('name', '=', data.get("chatID"))], limit=1)
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
        to_json = False
        try:
            to_json = answer.json()
            return to_json
        except Exception as e:
            _logger.info("Debug::: Chat API responded with an Error: ")
            _logger.info(e)
            return to_json

    # current company - Get current company
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
            # Number formatting to Kenyan format

    def format_number_to_KE(self, phone):
        # length
        if len(phone) > 13 and len(phone) < 10:
            return False
        # starts with 254
        if phone.startswith('254'):
            new_phone = phone
            formated_phone = new_phone
            return formated_phone
        # starts with zero
        elif phone.startswith('0'):
            new_phone = phone.lstrip('0')
            new_phone = '254' + new_phone
            formated_phone = new_phone
            return formated_phone
        # starts with +
        elif phone.startswith('+254'):
            formated_phone = phone.lstrip('+')
            return formated_phone
        # whatever
        else:
            # send to any number starting with +
            if phone.startswith('+'):
                formated_phone = phone.lstrip('+')
                return formated_phone
            else:
                return phone
    # generate whatsappp messages to send later
    def create_whatsapp_message_from_mailing_list_set_to_cron(self):

        _logger.info("Debug::: create_whatsapp_message_from_mailing_list_set_to_cron")
        for mailing in self.env['mailing.mailing'].search([('state','=','done'),('redis_sent','=',False)],limit=1):
            _logger.info("Debug:: Now in the loop")
            #if not res_ids:
            res_ids = mailing._get_remaining_recipients()
            if not res_ids:
                raise UserError(_('There are no recipients selected.'))
            # custom whatsapp functionality
            if mailing.send_via_whatsapp:
                _logger.info("Debug:: We override this and send messages usings whatsapp if enabled")
                # get contact list to send to
                # contact = self.env['mailing.contact'].search([('id','in',res_ids),
                #                                               ('whatsapp_sent','=',False)],limit=2000)
                contact = self.env['mailing.contact'].search([('id', 'in', res_ids)], limit=2000)
                # We have to get the company id to use to send message so that users can share same database
                message_owner_id = mailing.user_id.id
                company_to_use = self.env['res.users'].search([('id','=',message_owner_id)])
                if not company_to_use:
                    raise UserError(_('Message is missing Company Id to use. This is used for separating messages! Contact Support'))
                ## get the account to use
                _logger.info("Debug:: Company to use to send messages:::: {0}".format(company_to_use.company_id.id))
                chatapi_settings = self.env['chat.api.setup'].search([('chatapi_state', '=', True),('company_id','=',company_to_use.company_id.id)], limit=1)
                if not chatapi_settings:
                    raise UserError(
                        _('Please add chat api settings! Cannot send message without chat api set up complete.'))
                for item in contact:

                    # get message to send and banner URL
                     #convert_phone = self.format_number_to_KE(item.mobile)
                     convert_phone = item.mobile
                     _logger.info("Debug::: Phone number to send information to >>>>> {0}".format(convert_phone))
                     if convert_phone:
                        #test = self.send_message(convert_phone,self.body_plaintext)
                        ###
                        chatID = chatapi_settings.name
                        _logger.info("Debug::: Chat Name is ::: {0}".format(chatID))
                        image_link = mailing.banner_url
                        file_name = 'poster.jpeg'
                        caption_text = mailing.body_plaintext.format(item.name)

                        # only send image file if we have a link to the banner
                        if mailing.send_via_cron: # we want to send via a cron task
                            if image_link :
                                # we want to avoid sending message immediately otherwise we risk getting spammed
                                # we save this message and send later
                                media_message = self.env['whatsapp.media.message'].create({
                                    'name': convert_phone,
                                    'message_tag_content': caption_text,
                                    'message_public_image_link': image_link,
                                    'category': mailing.category.name,
                                    'state': 'tosend',
                                    'source_message': mailing.id,
                                    'company_id': chatapi_settings.company_id.id
                                })
                                # to disable
                                #send_file = self.send_a_file(chatID, convert_phone,image_link, file_name, caption_text)
                                _logger.info("Debug::: NOTICE!!!! Save messages to send later : ")
                                #_logger.info(send_file)
                            else:
                                #send_message_only = self.send_message(convert_phone, self.body_plaintext)
                                media_message = self.env['whatsapp.plain.message'].create({
                                    'name': convert_phone,
                                    'message_tag_content': caption_text,
                                    'state': 'draft',
                                    'source_message': mailing.id,
                                    'company_id': chatapi_settings.company_id.id
                                })
                                _logger.info("Debug::: Send normal text message without banner")
                                # set as sent via whatapp
                                item.whatsapp_sent = True
                        else:
                            _logger.error("Error:::: Could not format phone number {0}".format(item.mobile))
    # process message and send it then mark as sent. this is to avoid anti-spam system
    def whatsapp_media_processing(self):
        _logger.info("Debug::: Current Logged in User is {0}".format(self.env.user.id))
        if self.env.user.id == 1:
            self.odoo_bot_whatsapp_media_processing()
        else:
            try:
                current_company = self.get_current_company_value()
                domain = [('state','=','draft'),('company_id','in',current_company)]
            except Exception as e:
                _logger.error("An error occured in whatsapp_plain_processing(): {0}".format(e))
                current_company = self.env.company.id
                domain = [('state','=','draft'),('company_id','=',current_company)]

            browse_messages = self.env['whatsapp.media.message'].search(domain,limit=10)
            _logger.info("Debug::: Sending media messages...")
            _logger.info(browse_messages)
            chatapi_settings = self.env['chat.api.setup'].search([('chatapi_state', '=', True)], limit=1)
            if not chatapi_settings:
                raise UserError(_('Please add chat api settings! Cannot send message without chat api set up complete.'))
            for item in browse_messages:
                send_file = self.send_a_file(chatapi_settings.name, item.name, item.message_public_image_link, 'banner.jpeg', item.message_tag_content)
                _logger.info("Debug::: WhatsApp response")
                _logger.info(send_file)
                if send_file.get('sent'):
                    # change the status
                    item.state = 'sent'
                    item.status_message = send_file.get('message') +" : "+ send_file.get('description')
                    item.status_message_technical = send_file
                else:
                    item.state = 'failed'
                    item.status_message = send_file.get('message') + " : " + send_file.get('description')
                    item.status_message_technical = send_file
    # receive data in rabbitmq and pass it to the function responsible for connecting to chat api
    # https://stackoverflow.com/questions/34534178/rabbitmq-how-to-send-python-dictionary-between-python-producer-and-consumer
    def rabbitmq_receive(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='chat_text', durable=False)
        _logger.info(' [*] Waiting for messages. To exit press CTRL+C')

        def callback(ch, method, properties, body):
            #_logger.info(" [x] Received %r" % json.loads(body))
            #_logger.info(" [x] Done")
            to_json = json.loads(body)
            send_file = self.send_a_file(to_json.get('chatID'), to_json.get('phone'), to_json.get('body'),
                                          'banner.jpeg', to_json.get('caption'))
            if send_file:
                send_state = 'failed'
                if send_file.get('sent'):
                    send_state = 'sent'
                _logger.info("Debug::: Create Report Rabbitmq")
                data_to_create = {
                    'name': to_json.get('chatID') ,
                    'phone': to_json.get('phone'),
                    'message': to_json.get('body') ,
                    'caption_text': to_json.get('caption_text') ,
                    'send_state' : send_state,
                    'status_message': send_file

                }
                _logger.info(data_to_create)
                create_report = self.env['whatsapp.rabbit.queue'].sudo().create(data_to_create)
                #https://www.odoo.com/forum/help-1/how-to-insert-records-from-model-use-self-env-create-98309
                self.env.cr.commit()
                _logger.info("Debug:: Report ID created {0}".format(create_report))

            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        #channel.basic_consume(callback)
        channel.basic_consume(queue='chat_text', on_message_callback=callback)

        channel.start_consuming()
    # define rabbitmq sender
    def rabbitmq_send(self,chatID,phone,body,filename,caption):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='chat_text')
        message = {'chatID': chatID, 'phone': phone,
                   'body': body,
                   'filename': filename,
                   'caption': caption
                   }

        channel.basic_publish(exchange='',
                              routing_key='chat_text',
                              body=json.dumps(message),
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))
        _logger.info(" [x] Sent 'CHAT TEXT'")
        #connection.close()
    # redis publisher
    def redis_publisher(self,chatID,phone,body,filename,caption,token):
        redis_conn = redis.Redis(charset="utf-8", decode_responses=True)
        data = {
                   'chatID': chatID, 'phone': phone,
                   'token': token,
                   'body': body,
                   'filename': filename,
                   'caption': caption
            }
        redis_conn.publish("broadcast_to_users", json.dumps(data))
    # redis subscriber
    def redis_subscriber(self):
        # connection
        redis_conn = redis.Redis(charset="utf-8", decode_responses=True)
        pubsub = redis_conn.pubsub()
        pubsub.subscribe("broadcast_to_users")
        _logger.info("Debug:::: Iterate >>>>")
        for message in pubsub.listen():
            if message.get("type") == "message":
                to_json = json.loads(message.get("data"))
                _logger.info(to_json)
                # we send data to chat api
                #to_json = json.loads(body)
                send_file = self.send_a_file(to_json.get('chatID'), to_json.get('phone'), to_json.get('body'),
                                             'banner.jpeg', to_json.get('caption'))
                _logger.info("debug: After sending information")
                _logger.info(send_file)
                if send_file:
                    send_state = 'failed'
                    if send_file.get('sent'):
                        send_state = 'sent'
                    _logger.info("Debug::: Create Report Redis")
                    data_to_create = {
                        'name': to_json.get('chatID'),
                        'phone': to_json.get('phone'),
                        'message': to_json.get('body'),
                        'caption_text': to_json.get('caption_text'),
                        'send_state': send_state,
                        'status_message': send_file

                    }
                    _logger.info(data_to_create)
                    create_report = self.env['whatsapp.redis.queue'].sudo().create(data_to_create)
                    # https://www.odoo.com/forum/help-1/how-to-insert-records-from-model-use-self-env-create-98309
                    self.env.cr.commit()
                #print("message id: %s" % message.sid)

    def odoo_bot_redis_whatsapp_media_processing(self):
        messages = self.env['whatsapp.media.message'].search([('state', '=', 'tosend')], limit=5000)
        for item in messages:
            # get chat api instance to use
            chatapi_settings = self.env['chat.api.setup'].search(
                [('chatapi_state', '=', True), ('company_id', '=', item.company_id.id)], limit=1)
            # send_file = self.send_a_file(chatapi_settings.name, item.name, item.message_public_image_link,
            #                              'banner.jpeg', item.message_tag_content)
            _logger.info("DEBUG:::: REDIS PUBLISHER!: Chat API to use {0}".format(chatapi_settings.name))
            self.redis_publisher(chatapi_settings.name,item.name, item.message_public_image_link,
                                         'banner.jpeg', item.message_tag_content,chatapi_settings.chatapi_access_token)
            # To achieve target set to sent
            #if send_file.get('sent'):
            # _logger.info("Debug::: WhatsApp response")
            # _logger.info(send_file)
            # # change the status
            item.state = 'sent'
            item.status_message = 'Processed by Redis'
            item.status_message_technical = 'Redis processing'
            ## now we need to update that we have sent the message to avoid duplication
            browse_source = self.env['mailing.mailing'].search([('id','=',item.source_message.id)])
            if browse_source:
                # mark the message as sent to avoid creation
                browse_source.write({'redis_sent': True})
    # odoo bot processing messages
    def odoo_bot_whatsapp_media_processing(self):
            messages = self.env['whatsapp.media.message'].search([('state', '=', 'draft')], limit=20000)
            for item in messages:
                # get chat api instance to use
                chatapi_settings = self.env['chat.api.setup'].search(
                    [('chatapi_state', '=', True), ('company_id', '=', item.company_id.id)], limit=1)
                # send_file = self.send_a_file(chatapi_settings.name, item.name, item.message_public_image_link,
                #                              'banner.jpeg', item.message_tag_content)
                _logger.info("DEBUG:::: CONNECT TO RABBITMQ!")
                self.rabbitmq_send(chatapi_settings.name,item.name, item.message_public_image_link,
                                             'banner.jpeg', item.message_tag_content)
                # To achieve target set to sent
                #if send_file.get('sent'):
                # _logger.info("Debug::: WhatsApp response")
                # _logger.info(send_file)
                # # change the status
                item.state = 'sent'
                item.status_message = 'Sent to the Queue'
                item.status_message_technical = 'Message queued'
                _logger.info("Debug:: Update to SENT!!!!")
                #_logger.info("Debug::: WhatsApp response")
                #_logger.info(send_file)
                # if send_file:
                #     if send_file.get('sent'):
                #         # change the status
                #         item.state = 'sent'
                #         item.status_message = send_file.get('message') + " : " + send_file.get('description')
                #         item.status_message_technical = send_file
                #         _logger.info("Debug:: Update to SENT!!!!")
                #     else:
                #         item.state = 'failed'
                #         item.status_message = send_file
                #         item.status_message_technical = send_file
                # else:
                #     item.state = 'failed'
                #     item.status_message = "API Returned an error"
                #     item.status_message_technical = send_file
class WhatsappRabbitQueue(models.Model):
    _name = 'whatsapp.rabbit.queue'
    _description = "Rabbit Queue responses"

    name = fields.Char(string='ChatID')
    phone = fields.Char(string='Phone')
    message = fields.Char(string='Message')
    caption_text = fields.Char(string='Caption Text')
    send_state = fields.Char(string='Send State')
    status_message = fields.Char(string='Status Message')
# redis
class WhatsappRedisQueue(models.Model):
    _name = 'whatsapp.redis.queue'
    _description = "Redis Queue responses"

    name = fields.Char(string='ChatID')
    phone = fields.Char(string='Phone')
    message = fields.Char(string='Message')
    caption_text = fields.Char(string='Caption Text')
    send_state = fields.Char(string='Send State')
    status_message = fields.Char(string='Status Message')

