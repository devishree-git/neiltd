# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'NEI Account',
    'version': '1.1',
    'category': 'Invoicing Management',
    'summary': 'Account Report',
    'description': """
        NEI Account Report
    """,
    'depends': ['account'],
    'data': [
        'report/custom_header.xml',
        'report/invoice_report.xml',
        'report/invoice_report_templates.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False
}
