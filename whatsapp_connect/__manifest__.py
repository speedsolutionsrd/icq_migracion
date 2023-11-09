# -*- coding: utf-8 -*-
{
    'name': 'Whatsapp Connect Base',
    'category': '',
    'summary': 'Whatsapp Connect',
    'website': 'https://www.icq24.com',
    'author': 'Angstrom Mena',
    'version': '1.0',
    'description': """
Whatsapp Connector
=======================
        """,
    'depends': ['base'],
    'installable': True,
    'data': [
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "views/send_message_view.xml",
        "views/res_partner_views.xml"
    ],
    'auto_install': False,
}
