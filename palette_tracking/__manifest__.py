# -*- coding: utf-8 -*-
{
    'name': "Palette Tracking",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Khaled Habib",
    'category': 'Uncategorized',
    'version': '14.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'stock', 'sale_stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/palette_tracking_view.xml',
        'views/res_partner_inh.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
