# -*- coding: utf-8 -*-
{
    'name' : 'Website Bridetobe Statistics',
    'version' : '1.1',
    'summary': 'Manage statistics for Bridetobe',
    'sequence': 30,
    'description': """""",
    'author':"Angstrom Mena",
    'website': "http://www.icq24.com",
    'depends' : ['website_bridetobe','stock','website_bridetobe_comisiones'],
    'data': [
        "views/sale_rental.xml",
        "views/cancels.xml",
        "views/sales.xml",
        "views/products.xml",
    ],
    'installable': True,
}
