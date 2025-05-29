from odoo import models, fields, api


class Membermember(models.Model):
    _name = 'unamhe.member.member'
    _description = 'Member Record'
    _inherits = {'res.partner': 'partner_id'}

    S_TYPE = [
        ('self', 'Self Sponsor'),
        ('company', 'Company Sponsor'),
    ]

    partner_id = fields.Many2one('res.partner', ondelete="cascade", required=True)
    sponsorship_type = fields.Selection(S_TYPE, string="Sponsorship Type")
