# -*- coding: utf-8 -*-
{
    'name': 'Whatsapp Connect Chat Api',
    'category': '',
    'summary': 'Whatsapp Connect Chat Api',
    'website': 'https://www.icq24.com',
    'author': 'Angstrom Mena',
    'version': '1.0',
    'description': """
Whatsapp Connector Chat Api
=======================
        """,
    'depends': ['base', 'whatsapp_connect'],
    'installable': True,
    'data': [
        'views/res_config_settings.xml',
        'wizard/whatsapp_account_validation_view.xml'
    ],
    'auto_install': False,
}
