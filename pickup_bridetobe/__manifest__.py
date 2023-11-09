{
    "name": "Pickup Bridetobe",
    "summary": "",
    "version": "10.0.0.0.0",
    "category": "",
    "website": "https://www.icq24.com",
    "description": "",
    "author": "Escarly Dominguez, ICQ24",
    "license": "LGPL-3",
    "installable": True,
    "depends": ['website_bridetobe', 'pickup', 'website_bridetobe_comisiones'],
    "data": [
        'web_template/seller_views.xml',
        # 'views/website_templates.xml',
        'views/view_comision_payment.xml',
        'views/pickup_view.xml',
        'views/pickup_commission_view.xml',
        'views/sale_order_view.xml',
        'views/sale_rental.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'pickup_bridetobe/static/src/js/pickup_rental.js'
        ],
    }
}
