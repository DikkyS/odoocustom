# product_request_management/__manifest__.py
{
    'name': 'Product Request Management',
    'version': '1.0',
    'category': 'Tools',
    'author': 'Dikky Suryadi',
    'summary': 'Manage product requests and purchase orders',
    'depends': ['base', 'stock', 'purchase'],  # Add any additional dependencies needed
    'data': [
        'data/product_request_data.xml',
        'views/product_request_views.xml',
        'controllers/custom_controller.py',
        'controllers/product_request_api.py',
        'security/ir.model.access.csv',
        'views/request_detail_views.xml',
        'views/product_request_menu.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'demo': [],
    'images': [],
    'qweb': [],
    'models': [
        'models/product_request.py',
        'models/request_detail.py',
        'models/product_request_stage.py',  # Add the new models file here if you have one
    ],
}
