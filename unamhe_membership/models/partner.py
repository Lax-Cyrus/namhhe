# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from . import membership


class Partner(models.Model):
    _inherit = 'res.partner'
    _order = 'id DESC'

    RELIGION = [
        ('Catholic', 'Catholic'),
        ('Anglican', 'Anglican'),
        ('Pentecostal', 'Pentecostal'),
        ('Protestant', 'Protestant'),
        ('Muslim', 'Muslim'),
        ('SDA', 'SDA'),
        ('Other', 'Other'),
    ]

    GENDER = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]

    associate_member = fields.Many2one('res.partner', string='Associate Member',
                                       help="A member with whom you want to associate your membership."
                                            "It will consider the membership state of the associated member.")
    member_lines = fields.One2many('membership.membership_line', 'partner', string='Membership')
    free_member = fields.Boolean(string='Free Member', help="Select if you want to give free membership.")
    membership_amount = fields.Float(string='Membership Amount', digits=(16, 2), help='The price negotiated by the partner')
    membership_state = fields.Selection(membership.STATE, compute='_compute_membership_state', default="none",
                                        string='Current Membership Status', store=True, recursive=True,
                                        help='It indicates the membership state.\n'
                                             '-Non Member: A partner who has not applied for any membership.\n'
                                             '-Cancelled Member: A member who has cancelled his membership.\n'
                                             '-Old Member: A member whose membership date has expired.\n'
                                             '-Waiting Member: A member who has applied for the membership and whose invoice is going to be created.\n'
                                             '-Invoiced Member: A member whose invoice has been created.\n'
                                             '-Paying member: A member who has paid the membership fee.')
    membership_start = fields.Date(compute='_compute_membership_state',
                                   string='Membership Start Date', store=True,
                                   help="Date from which membership becomes active.")
    membership_stop = fields.Date(compute='_compute_membership_state',
                                  string='Membership End Date', store=True,
                                  help="Date until which membership remains active.")
    membership_cancel = fields.Date(compute='_compute_membership_state',
                                    string='Cancel Membership Date', store=True,
                                    help="Date on which membership has been cancelled")
    # unamhe fields
    membership_id = fields.Char(string='Membership Number')
    online_creation = fields.Boolean(string='Created Online')
    date_of_birth = fields.Date('Date of Birth')
    gender = fields.Selection(GENDER)
    religion = fields.Selection(RELIGION, string="Religion")
    marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('separated', 'Separated'), ('divorced', 'Divorced')])
    product = fields.Many2one('product.product', string="Type", domain="[('membership_member_type','in',('individual','corporate'))]")
    product_price = fields.Float(string="Price")

    current_employer = fields.Char('Current Employer')
    current_position = fields.Char('Position At Work')
    employee_address = fields.Text("Postal Address of Employer")
    employement_history = fields.Text("Employment History")
    insurance_training = fields.Text("Insurance Training")
    events_attended = fields.Text("Major Events Attended")
    awards_received = fields.Text("Insurance Awards Received")
    other_qualification = fields.Char("Other Qualification")
    member = fields.Boolean()
    academic_documents = fields.Binary('Academic Documents')
    other_academic_documents = fields.Binary(string="Other Qualifications", required=False)
    insurance_qualification = fields.Selection([('cop', 'COP'), ('certificate', 'Certificate'), ('diploma', 'Diploma'),
                                                ('advanced', 'Advanced Diploma'), ('other', 'Other')])
    personal_statement = fields.Binary(string="Personal Statement")
    # barcode = fields.Binary('Barcode', compute="_compute_generate_barcode", store=True)

    MEMBER_TYPE = [
        ('person', 'Individual'),
        ('company', 'Corporate'),
    ]

    ORGAN_T = [
        ('insurance', 'Insurance Company'),
        ('brokers', 'Brokers'),
        ('banks', 'Banks'),
        ('health_memb', 'Health Membership Organisation'),
        ('re_insurance', 'Re-Insurance Companies'),
        ('loss_assessors', 'Loss Assessors / Adjusters, Surveyors & Engineering Valuers'),
        ('corporate_agencies', 'Corporate Agencies'),
        ('other', 'Other'),
    ]

    organisation_type = fields.Selection(ORGAN_T, string="Organisation Type")
    company_ceo = fields.Char("Company CEO", tracking=True)
    company_ceo_tel = fields.Char("Company CEO Telephone", tracking=True)
    ceo_email = fields.Char("Company CEO Email", tracking=True)
    company_cordinator = fields.Char("Company Coordinator", tracking=True)
    company_cordinator_tel = fields.Char("Coordinator Telephone", tracking=True)
    company_cordinator_email = fields.Char("Coordinator Email", tracking=True)
    company_type = fields.Selection(MEMBER_TYPE)
    sponsored_students = fields.One2many('op.student.sponsors', 'sponsor', string="Sponsored Students")
    students_sponsored = fields.One2many('op.student.sponsors', 'student', string="Students Sponsored")
    cpd_points = fields.One2many('cpd.point.register', 'member', string="CPD Points")
    member_type = fields.Selection(MEMBER_TYPE, string="Member Type", related="company_type")
    

    _sql_constraints = [
        ('unique_membership_id',
         'unique(membership_id)', 'Membership ID should be unique!')]

    @api.depends('member_lines.account_invoice_line',
                 'member_lines.account_invoice_line.move_id.state',
                 'member_lines.account_invoice_line.move_id.payment_state',
                 'member_lines.account_invoice_line.move_id.partner_id',
                 'free_member',
                 'member_lines.date_to', 'member_lines.date_from',
                 'associate_member', 'associate_member.membership_state')
    def _compute_membership_state(self):
        today = datetime.utcnow().date()
        for partner in self:
            membership_history = partner.member_lines
            membership_years = [int(y.date_to.year) for y in membership_history if y.date_to.year >= today.year]
            member_lines = [l for l in membership_history if l.date_to.year == max(membership_years)]

            partner.membership_stop = datetime(max(membership_years), 12, 31).date() if len(membership_years) > 0 else False
            if not partner.membership_start:
                partner.membership_stop = today

            if len(member_lines) > 0:
                for mline in member_lines:
                    if mline.member_type == partner.product.product_tmpl_id.membership_member_type and mline.date_to.year == max(membership_years):
                        partner.membership_state = mline.state
                        break

            if len(partner.member_lines) > 0 == len(member_lines):
                partner.membership_state = 'old'
            elif len(partner.member_lines) == 0:
                partner.membership_state = 'none'

    def checkMemberStatus(self):
        today = datetime.utcnow().date()
        if len([int(y.date_to.year) for y in self.member_lines if y.date_to.year >= today.year]) > 0:
            return "ACTIVE"
        return "INACTIVE"

    def checkMemberRenewalStatus(self):
        if self.checkMemberStatus() == 'INACTIVE':
            return 'INACTIVE'

        if datetime.utcnow().date().month in [10, 11, 12]:
            return "INACTIVE"

        return "ACTIVE"

    @api.constrains('associate_member')
    def _check_recursion_associate_member(self):
        for partner in self:
            level = 100
            while partner:
                partner = partner.associate_member
                if not level:
                    raise ValidationError(_('You cannot create recursive associated members.'))
                level -= 1

    @api.model
    def _cron_update_membership(self):
        partners = self.search([('membership_state', 'in', ['invoiced', 'paid'])])
        # mark the field to be recomputed, and recompute it
        self.env.add_to_compute(self._fields['membership_state'], partners)

    def printMembershipID(self):
        if self.id:
            return {
                'type': 'ir.actions.act_url',
                'url': '/ieg/generate_doc/MEMBERSHIP_ID_CARD/%s' % (self.id),
                'target': 'self',
            }

    # def printMemberCertificate(self):
    #     if self.id:
    #         return {
    #             'type': 'ir.actions.act_url',
    #             'url': '/ieg/generate_doc/CORPORATE_MEMBER_CERTIFICATE/%s' % (self.id),
    #             'target': 'self',
    #         }
    def print_member_certificate(self):
        """Method to trigger the Member Certificate report."""
        return self.env.ref('unamhe_membership.action_report_member_certificate').report_action(self)
    
    def action_activate_member(self):
        for partner in self:
            partner.membership_state = 'paid'

    def create_membership_invoice(self, product, amount):
        """ Create Customer Invoice of Membership for partners.
        """
        invoice_vals_list = []
        for partner in self:
            addr = partner.address_get(['invoice'])
            if partner.free_member:
                raise UserError(_("Partner is a free Member."))
            if not addr.get('invoice', False):
                raise UserError(_("Partner doesn't have an address to make the invoice."))

            invoice_vals_list.append({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_line_ids': [
                    (0, None, {'product_id': product.id, 'quantity': 1, 'price_unit': amount,
                               'tax_ids': [(6, 0, product.taxes_id.ids)]})
                ]
            })

        return self.env['account.move'].create(invoice_vals_list)



