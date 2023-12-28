{
    'name': 'Sale Order Tax Summary',
    'version': '15.0',
    'category': 'Sale',
    'summery': 'Show tax details in sale order',
    'author': 'INKERP',
    'website': "https://www.INKERP.com",
    'depends': ['sale_management'],
    
    'data': [
        'views/sale_order_view.xml',
        'security/ir.model.access.csv'
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
