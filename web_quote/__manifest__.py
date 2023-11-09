# -*- coding: utf-8 -*-
{
    'name': 'Web Quotes',
    'category': '',
    'summary': 'Web Quotes',
    'website': 'https://www.icq24.com',
    'author': 'Angstrom Mena',
    'version': '1.0',
    'description': """
Web Quotes
=======================
        """,
    'depends': ['sale', 'base', 'website'],
    'installable': True,
    'data': [
        'web_views/search_partner.xml',
        'web_views/partner_details.xml',
        'web_views/partner_list.xml',
        'web_views/quote_items.xml',
        'web_views/quote_confirmation.xml',
        # 'web_views/website_menu.xml',
    ],
    'application': False,
}