{
    'name': 'Survey Bridetobe',
    'description': 'Sends message to fill survey',
    'category': 'Website',

    'version': '10.0.0.0.0',
    'author': 'ICQ24',
    'depends': ['base', 'mail', 'contacts', 'survey', 'sale', 'sales_team', 'stock', 'website_bridetobe'],
    'data': ['views/survey_bridetobe_view.xml',
             'wizard/send_survey_wizard_view.xml',
             'views/sale_rental.xml',
             'wizard/survey_email_compose_message.xml'],
    'instalable': True,
    'auto_install': False,
    'application': False
}
