from odoo import fields,models,api,_
import logging
_logger = logging.getLogger(__name__)
import requests
from odoo.exceptions import UserError
import json

class MassMailingSMSExtend(models.Model):
    _inherit = 'mailing.mailing'
    send_via_cron = fields.Boolean(string='Send on Cron',default=True)
    category = fields.Many2one('marketing.message.groups',string='Target Group',required=False)
    message_type = fields.Selection([('image_message', 'Image & Text'), ('text_only', 'Text Only'),
                                     ('video_text', 'Video & Text')], string='Message Type', default='image_message',
                                    help='This helps in connecting with the correct WhatsApp endpoint',required=True)
    banner_url = fields.Char(string='Add Banner URL',default='Click Save to Add url first',required=True,help='Use this to send an Image File with message.')
    send_via_whatsapp = fields.Boolean(string='Send Via WhatsApp', default=True,
                                       help='Set this to override SMS configuration and request API to send message via WhatsApp')
    redis_sent = fields.Boolean(string='Redis Sent', help='To avoid multiple creation of these messages and sending, when redis sends, mark message as sent to avoid resending')
    # onchange for medium type
    # TODO - For now only support SMS,WhatsApp
    # utility
    # Number formatting to Kenyan format
    def format_number_to_KE(self, phone):
        # length
        if len(phone) > 13 and len(phone) < 10:
            _logger.info("Error: The phone number {0} is invalid!!".format(phone))
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
    # We override this sending function and send sms via whatsApp
    def action_send_sms(self, res_ids=None):
        # get settings
        chatapi_settings = self.env['chat.api.setup'].search([('chatapi_state','=',True)],limit=1)
        if not chatapi_settings:
            raise UserError(_('Please add chat api settings! Cannot send message without chat api set up complete.'))
        self.write({'state': 'done', 'sent_date': fields.Datetime.now()})
        # for mailing in self:
        #     if not res_ids:
        #         res_ids = mailing._get_remaining_recipients()
        #     if not res_ids:
        #         raise UserError(_('There are no recipients selected.'))
        #     # custom whatsapp functionality
        #     if self.send_via_whatsapp:
        #         _logger.info("Debug:: We override this and send messages usings whatsapp if enabled")
        #         # get contact list to send to
        #         contact = self.env['mailing.contact'].search([('id','in',res_ids),
        #                                                       ('whatsapp_sent','=',False)])
        #         #print(contact)
        #         for item in contact:
        #
        #             # get message to send and banner URL
        #              convert_phone = self.format_number_to_KE(item.mobile)
        #              if convert_phone:
        #                 #test = self.send_message(convert_phone,self.body_plaintext)
        #                 ###
        #                 chatID = chatapi_settings.name
        #                 image_link = self.banner_url
        #                 file_name = 'poster.jpeg'
        #                 caption_text = self.body_plaintext.format(item.name)
        #                 _logger.info("Debug:: Test banner link >>> {0}".format(image_link))
        #                 # only send image file if we have a link to the banner
        #                 if not self.send_via_cron: # we want to send via a cron task
        #                     if image_link :
        #                         # we want to avoid sending message immediately otherwise we risk getting spammed
        #                         # we save this message and send later
        #                         media_message = self.env['whatsapp.media.message'].create({
        #                             'name': convert_phone,
        #                             'message_tag_content': caption_text,
        #                             'message_public_image_link': image_link,
        #                             'category': self.category,
        #                             'state': 'tosend'
        #                         })
        #                         # to disable
        #                         #send_file = self.send_a_file(chatID, convert_phone,image_link, file_name, caption_text)
        #                         _logger.info("Debug::: Save messages to send later : ")
        #                         #_logger.info(send_file)
        #                     else:
        #                         #send_message_only = self.send_message(convert_phone, self.body_plaintext)
        #                         media_message = self.env['whatsapp.plain.message'].create({
        #                             'name': convert_phone,
        #                             'message_tag_content': caption_text,
        #                             'state': 'draft'
        #                         })
        #                         _logger.info("Debug::: Send normal text message without banner")
        #         # mark as done
        #         mailing.write({'state': 'done', 'sent_date': fields.Datetime.now()})
        #                 # Activate this if you want  to send only once
        #                 # if test_send_file.get('sent'):
        #                 #     item.whatsapp_sent = True
        #                 # else:
        #                 #     _logger.info('Debug:: Message already sent to {0}'.format(convert_phone))
        #         # mark message as done with sending
        #         #mailing.write({'state': 'done', 'sent_date': fields.Datetime.now()})
        #
        #
        #     else:
        #       composer = self.env['sms.composer'].with_context(active_id=False).create(mailing._send_sms_get_composer_values(res_ids))
        #       composer._action_send_sms()
        #       mailing.write({'state': 'done', 'sent_date': fields.Datetime.now()})



        return True


class MailingContactExtend(models.Model):
    _inherit='mailing.contact'

    whatsapp_sent = fields.Boolean(string='WhatsApp Sent',default=False,
                                   help='Set this to mark contact as to have received the message')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
class MailingListExtend(models.Model):
    _inherit='mailing.list'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
