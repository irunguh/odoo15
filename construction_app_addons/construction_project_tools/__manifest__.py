# -*- coding: utf-8 -*-
##############################################################################
# Construction Project Management
#  2020 AmkaTek Limited <amkatekconsulting@gmail.com>
#
##############################################################################

{
    "name": "Construction Project Management ",
    'version': '15.0.1.0.0',
    "author": "AmkaTek Limited",
    "website": "https://amkatek.com",
    "description": """
     Modify Odoo Project module to capture and manage construction project management elements
     This module will include all missing features for construction project management in the default Odoo project management
     *** Features ***
     1.Budget Creation and Management
     2. Project Site Management
     3. Budget comparisions with Actual Project Expenses
     4. Materials, Labour requisitions
     5. Project Expenses
     6. Addition Reporting
    """,

    "category": "Project",
    "depends": [
        'project','hr_expense','hr_expense_petty_cash','stock','sale'
    ] ,

    "data": [
        'wizard/sales_order_request_views.xml',
        'views/site_materials_request.xml',
        'views/project.xml', # we are overriding the default project view and we add custom stuffs
        'views/project_budget.xml',
        'views/project_budget_sequence.xml',
        'views/stock_project.xml',
        'views/project_consume_materials.xml',
        'views/projects_menu.xml',
        'security/project_budget_security.xml',
        'security/ir.model.access.csv',
        'views/sales.xml',




    ],
    'assets': {
        'assets': [
        ],
        'web.assets_qweb': [

        ],
    },
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
