# -*- coding: utf-8 -*-
{
    'name': "Bridetobe Vestidores",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        ICQ24 Website Bridetobe
    """,

    'author': "Jose Artigas",
    'website': "https://www.icq24.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'website',
        'website_bridetobe'
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/website_main.xml',
        'views/view_vestidores.xml',
        'views/website_modista.xml',
        'views/website_partner.xml',
        'views/website_queue_making.xml',
        'views/website_queue_test.xml',
        'views/website_queue_tv.xml',
        'views/website_quotes.xml',
        'views/website_vestidores.xml',
        'views/res_config_view.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'rentq_vestidores/static/src/css/select2.min.css',
            'rentq_vestidores/static/src/css/style.css',
            'rentq_vestidores/static/src/css/jquery-ui.css',
            'rentq_vestidores/static/src/js/sweetalert.min.js',
            'rentq_vestidores/static/src/js/select2.min.js',
            'rentq_vestidores/static/src/js/responsivevoice.js',
            'rentq_vestidores/static/src/js/vestidores.js',
            'rentq_vestidores/static/src/js/jquery-ui.js',
            'rentq_vestidores/static/src/js/audio_tv.js',
            'rentq_vestidores/static/src/js/audio_modista.js',
            'rentq_vestidores/static/src/js/queues.js',
            
        ],
    },

    'demo': [
        'demo/demo.xml',
    ],
}
