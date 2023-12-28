# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payment Analytic Account and Analytic Tag',
    'version': '15.0.0.1',
    'category': 'Accounting',
    'summary': 'Payment Cost Center on Account Payment Analytic tag Payment with Analytic Account Payment with Analytic tag on payment analytic account on payment voucher with analytic account voucher with analytic tag internal payment transfer with analytic account',
    'description': """
			This odoo app helps user to add analytic account and analytic tags on payment, When payment is posted then selected analytic account and tag will passed on journal items, User also can add analytic account and tags while registering payment from invoice and selected analytic account and tags will passed on journal item and payment created for that. """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'price': 35,
    'currency': 'EUR',
    "depends": ['base', 'account'],
    "data": [
        'views/account_payment_inherit_views.xml',
        'wizard/inherited_account_payment_register_views.xml',
    ],
    'license':'OPL-1',
    'installable': True,
    "auto_install": False,
    "installable": True,
    'live_test_url': 'https://youtu.be/l6Duxetqi60',
    "images":["static/description/Banner.png"],
}
