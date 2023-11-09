# -*- coding: utf-8 -*-
{
    'name': 'Loyalty Cards',
    'category': '',
    'sequence': 50,
    'summary': 'Tarjetas de Lealtad',
    'website': 'https://www.icq24.com',
    'author': 'Angstrom Mena',
    'version': '1.0',
    'description': """
Loyalty Cards Managment
=======================
        """,
    'depends': ['base','sales_team','account'],
    'installable': True,
    'data': ['security/ir.model.access.csv',
             'views/loyalty_card_view.xml',
             'views/res_partner_view.xml',
             'views/loyalty_card_config_view.xml',
             'views/account_invoice_view.xml',
             'views/loyalty_card_point_view.xml',
             'wizard/loyalty_point_paid_view.xml',
             'data/default_payments.xml'],
    'application': False,
}