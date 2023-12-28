# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2020 AmkaTek Limited <amkatekconsulting@gmail.com>
#
##############################################################################

{
    "name": "MPESA Transactions Management",
    'version': '11.0.1.0.0',
    "author": "AmkaTek Limited",
    "website": "www.amkatek.com",
    "description": """
     - Record Client MPESA transactions. This allows one to monitor in realtime payments processed by LIPA na MPESA API
Functionality:
      - Monitor Pending Payment
      - View Paid transactions

    """,

    "category": "Property",
    "depends": [
        'mail',
        # 'product'
    ],

    "data": [
        'views/views.xml',
        'views/paybill_payments.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/paybill_cron.xml',
    ],
    'application': True,
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
