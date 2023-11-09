# -*- coding: utf-8 -*-
{
    'name': 'Website Bridetobe Notification',
    'category': 'bridetobe',
    'sequence': 50,
    'summary': 'Notification System for Bridetobe',
    'website': 'https://www.icq24.com',
    'author': 'Angstrom Mena',
    'version': '1.0',
    'description': """
ICQ24 Website Bridetobe Notification
=======================
        """,
    'depends': ['website_bridetobe', 'whatsapp_connect', 'mail', 'meta_connector'],
    'installable': True,
    'data': [
        "security/ir.model.access.csv",
        "views/sale_rental_custom_message_views.xml",
        "views/sale_rental_internal_state_views.xml",
        "views/res_config_view.xml",
        "wizards/sale_rental_send_custom_message_view.xml",

    ],
    'application': False,
}
