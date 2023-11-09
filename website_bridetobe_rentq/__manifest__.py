{
    "name": "Bridetobe RentQ",
    "summary": "",
    "version": "10.0.0.0.0",
    "category": "",
    "website": "https://www.icq24.com",
    "description": "",
    "author": "ICQ24",
    "license": "LGPL-3",
    "installable": True,
    "depends": ['website', 'website_bridetobe','web' ],
    "data": [
        'views/rentq_templates.xml',
        'views/assets_frontend.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'website_bridetobe_rentq/static/src/less/style_menu.less',
            'website_bridetobe_rentq/static/src/js/navbar_menu.js',
        ],
    }
}