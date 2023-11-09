# -*- coding: utf-8 -*-
{
    'name': 'Comisiones Bridetobe',
    'category': 'bridetobe',
    'sequence': 50,
    'summary': 'Comisiones for Bridetobe',
    'website': 'https://www.icq24.com',
    'author': 'Angstrom Mena',
    'version': '1.0',
    'description': """
ICQ24 Comisiones Bridetobe
=======================
        """,
    'depends': ['website_bridetobe','hr','sales_team'],
    'installable': True,
    'data': [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/view_tarifa_comision.xml",
        "views/view_comision.xml",
        "views/view_comision_payment.xml",
        "views/menu_items.xml",
        "reports/comision_payment_report.xml",
    ],
    'application': False,
}
