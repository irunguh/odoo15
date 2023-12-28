# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2020 AmkaTek Limited <amkatekconsulting@gmail.com>
#
##############################################################################

{
    "name": "MPESA Failed Payments ",
    'version': '11.0.1.0.0',
    "author": "AmkaTek Limited",
    "website": "www.amkatek.com",
    "description": """
     - Capture all notifications from MPESA that fail to record in the system
Functionality:
      - Record all transactions that fail from mpesa
      - The module will just be creating an entry of data from safaricom then we can view all transactions that fail 
      and recreate in the recording
    """,

    "category": "Sales",
    "depends": [
        'mail',
        # 'product'
    ],

    "data": [
        'views/failed_paybill_payments.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
       'data/paybillrepush_cron.xml',
    ],
    'application': True,
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
