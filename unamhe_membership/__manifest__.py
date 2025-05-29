# -*- coding: utf-8 -*-

{
    'name': 'Unamhe Membership & CPDS',
    'version': '0.1',
    'category': 'Sales,Membership',
    'description': """
This module, Based on Odoo Membership, allows you manage memberships.
=====================================================================

It supports different kind of members:
--------------------------------------
    * Free member
    * Associated member (e.g.: a group subscribes to a membership for all subsidiaries)
    * Paid members
    * Special member prices

It is integrated with sales and accounting to allow you to automatically
invoice and send propositions for membership renewal.
    """,
    'depends': [
        'account',
        'event',
        'event_sale',
        'portal',
        'website',
        'website_event',
        'event'
    ],
    'data': [
        'security/ir.model.access.csv',
        "security/security_group.xml",
        'wizard/membership_invoice_views.xml',
        'data/membership_data.xml',
        'data/email_data.xml',
        'views/product_views.xml',
        'views/partner_views.xml',
        'views/event_views.xml',
        'views/unamhe_memebership_webform.xml',
        'views/membership_application_view.xml',
        'views/member_portal.xml',
        'views/sponsor_application_courses.xml',
        'views/member_cpd_statement.xml',
        'views/certificate.xml',
        'report/report_membership_views.xml',
        'report/membership_invioce.xml',
        'report/report_membership_invoice_template.xml',
        'services/views/crons.xml',
        'views/cpd_certificate_report.xml',
        'views/cpd_register.xml',
        'views/application_form_views.xml',
        'views/application_form_menus.xml',
        'report/certificate_template.xml',
        'report/report_menu.xml',
    ],
    'assets': {
        'web.assets_common': [
            'unamhe_membership/static/src/css/**/*','unamhe_membership/static/src/js/scripts.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'website': '#',
    'license': 'LGPL-3',
    'application': True,
}
