# -*- coding: utf-8 -*-
{
    'name': 'Whatsapp Promotions',
    'category': '',
    'summary': 'Whatsapp Promotions',
    'website': 'https://www.icq24.com',
    'author': 'Angstrom Mena',
    'version': '1.0',
    'description': """
Whatsapp Promotions management
=======================
        """,
    'depends': ['base', 'whatsapp_connect', 'whatsapp_connect_chat_api'],
    'installable': True,
    'data': [
        "security/ir.model.access.csv",
        'views/whatsapp_promotion_view.xml',
        'views/whatsapp_promotion_list_view.xml',
        'views/res_partner_view.xml',
        'wizards/send_promotion_wizard.xml',
    ],
    'auto_install': False,
}
