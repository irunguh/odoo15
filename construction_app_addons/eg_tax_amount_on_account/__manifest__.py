{
    'name': 'Tax Amount on Account',
    'version': '15.0.0.0',
    'author': 'INKERP',
    'summary': 'Tax amount in Account Invoice.',
    'description': """This module helps to show Tax Amount in Account Invoice.""",
    'category': 'Account',
    'website': 'https://www.INKERP.com/',
    'depends': ['account'],
    
    'data': [
        'views/account_move_view.xml',
        'report/account_report_template.xml',
    ],
         
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
