# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2020 AmkaTek Limited <amkatekconsulting@gmail.com>
#
##############################################################################

{
    "name": "MPESA Query Bills ",
    'version': '11.0.1.0.0',
    "author": "AmkaTek Limited",
    "website": "www.amkatek.com",
    "description": """
     - Allow users to query bills from mpesa portal
     - The system will query bill status and only record if they are marked as completed from mpesa portal
     - The system can then consume this bill and register in paybill payments
     - This helps automate pulling of bills from mpesa without having to create the bills manually. 
    """,

    "category": "Sales",
    "depends": [
        'mail',
        'mpesa_payments_failed'
    ],

    "data": [
        'views/bills.xml',
        'wizard/pull_bills_wizard.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
       'data/pulled_bills_cron.xml',
    ],
    'application': True,
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
