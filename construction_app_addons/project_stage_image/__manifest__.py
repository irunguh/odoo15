{
    'name': 'Project Stage Image',
    'version': '15.0.1.0',
    'author': 'Kareem Abuzaid, kareem.abuzaid123@gmail.com, Boniface Irungu, amkatekconsulting@gmail.com',
    'website': 'https://kareemabuzaid.com',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'web',
    ],
    'data': [
        #'views/templates.xml',
        'views/project_task_type.xml',
    ],
    'images': ['static/description/icon.png'],
    'assets': {
        'web.assets_backend': [
            '/project_stage_image/static/src/js/kanban_column.js'
        ],
        'web.assets_qweb': [

        ]
    },
    'installable': True,
    'application': False,
}
