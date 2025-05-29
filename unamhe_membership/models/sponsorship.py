
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentSponsor(models.Model):
    _name = "op.student.sponsors"
    _description = "Sponsor"

    sponsor = fields.Many2one('res.partner', string='Sponsor', domain="[('is_company', '=', True)]", required=True)
    student = fields.Many2one('res.partner', string='Member', domain="[('is_company', '=', False)]", required=True)
    sponsored_activities = fields.One2many('account.move.line', 'for_partner_id', string='Sponsored Activities',
                                           domain="[('partner_id', '=', sponsor), ('for_partner_id', '=', student)]")
    relationship = fields.Char(string='Relationship')

    _sql_constraints = [
        ('unique_fields', 'unique(sponsor, student)', 'Fields Sponsor and Member must be unique set!')
    ]

    @api.constrains('sponsor', 'student')
    def _check_unique_fields(self):
        for record in self:
            # Check for uniqueness
            if record.sponsor and record.student:
                duplicate_records = self.search([
                    ('sponsor', '=', record.sponsor.id),
                    ('student', '=', record.student.id),
                    ('id', '!=', record.id),  # Exclude current record
                ])
                if duplicate_records:
                    raise ValidationError('Fields Sponsor and Member must be unique set!')
