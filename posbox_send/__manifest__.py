{
    "name": "Posbox Send",
    "category": '',
    "summary": """
        General
        Permite imprimir en el POSBOX fuera del modulo de POS
       """,
    "sequence": 1,
    'author': "Angstrom Mena",
    'website': "http://www.icq24.com",
    'version': '0.1',

    "depends": ['base','sales_team'],
    "data": [
        'views/posbox_send_view.xml',
        'views/posbox_print_test.xml',
        # 'views/web_assets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'posbox_send/static/src/js/posbox.js',
            'posbox_send/static/src/js/rsvp-3.1.0.min.js',
            'posbox_send/static/src/js/sha-256.min.js',
            'posbox_send/static/src/js/qz-tray.js'
        ],
    }
    # ,

    # "installable": True,
    # "application": False,
    # "auto_install": False,
}