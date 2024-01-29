{
    'name': 'sale_multi_db',
    'summary': 'data migration',
    'author': 'Aman',
    'license': 'LGPL-3',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/contact_inherit.xml',
        'views/contact_wizard.xml',
    ]
}