# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2021 AmkaTek Limited <amkatekconsulting@gmail.com>
#
##############################################################################

{
    "name": "Mass Mailing Extend",
    'version': '15.0',
    "author": "AmkaTek Limited",
    "website": "www.amkatek.com",
    "description": """
     - Extend default features of sms sending module and add option to allow one send messages via WhatsApp and Other Social 
     media integrations features. 
     """,

    "category": "Marketing",
    "depends": [
        'mass_mailing',
        'mass_mailing_sms',
        'crm',
        'base',
        #'project'
    ],

    "data": [
        'views/mailing_extend.xml',
        'views/whatsapp_media_message.xml',
        'views/whatsapp_plain_message.xml',
        'views/chat_api_setup.xml',
        'views/rabbit_queue_responses.xml',
        'views/redis_messages.xml',
        'views/whatsapp_customer_reply.xml',
        'views/marketing_message_groups.xml',
        'data/mass_whatsapp_cron.xml',
        'views/menus.xml',
        'views/other_menus.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
