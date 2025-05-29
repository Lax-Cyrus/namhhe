import datetime
import base64
from odoo import fields, api, models, _


class MembershipApplication(models.Model):
    _name = 'unamhe.membership.application'
    _description = 'Membership Application'
    _order = 'create_date DESC'
    _inherit = ['mail.thread']

    MEMBER_TYPE = [
        ('person', 'Individual'),
        ('company', 'Corporate'),
    ]

    GENDER = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    RELIGION = [
        ('Catholic', 'Catholic'),
        ('Anglican', 'Anglican'),
        ('Pentecostal', 'Pentecostal'),
        ('Protestant', 'Protestant'),
        ('Muslim', 'Muslim'),
        ('SDA', 'SDA'),
        ('Other', 'Other'),
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

    @api.model
    def _get_current_date(self):
        """:return current date """
        return fields.Date.today()

    def _get_default_company(self):
        company = self.env.company
        return company

    STATE = [
        ('draft', 'New Application'),
        ('approve', 'Submitted'),
        ('reject', 'Rejected'),
        ('approved', 'Approved'),
        ('registered', 'Registered'),
    ]
    APPROVAL = [
        ('approved', 'APPROVED'),
        ('rejected', 'REJECTED'),
    ]

    name = fields.Char("Number")
    member_name = fields.Char("Name")
    date = fields.Date("Date", default=lambda self: self._get_current_date())
    date_of_birth = fields.Date("Date Of Birth :")
    approval_date = fields.Date("Approval Date :")
    phone = fields.Char("Phone Number :")
    mobile = fields.Char("Mobile Number :")
    email = fields.Char("Email")
    image_1920 = fields.Binary("Passport Photo", attachment=True, store=True)
    user_id = fields.Many2one('res.users', 'User')
    company_id = fields.Many2one('res.company', 'Company', default=_get_default_company)
    job_title = fields.Char("Job Title :")
    public_service_grade = fields.Char("Public Service Grade :")
    home_email = fields.Char("Work Email :")
    work_date_assessed = fields.Date(string="Date Assessed")
    home_mobile = fields.Char("Work Telephone :")
    home_address = fields.Char("Physical Address :")
    city_work = fields.Many2one('unamhe.cities', string='City')
    district_work = fields.Many2one('unamhe.district', string="District")    
    level_membership = fields.Char("Level of Membership :")    
    marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('separated', 'Separated'), ('divorced', 'Divorced')])  
    current_employer = fields.Char('Current Employer')
    current_position = fields.Char('Position At Work')
    employee_address = fields.Text("Postal Address of Employer")
    employement_history = fields.Text("Employment History")
    insurance_training = fields.Text("Insurance Training")
    events_attended = fields.Text("Major Events Attended")
    awards_received = fields.Text("Insurance Awards Received")
    other_qualification = fields.Char("Other Qualification")
    academic_documents = fields.Binary('Insurance Documents')
    other_academic_documents = fields.Binary(string="Other Qualifications")
    product = fields.Many2one('product.product', 'Membership Category')
    corporate_product = fields.Many2one('product.product', 'Membership Category')
    move_id = fields.Many2one('account.move', string="Invoice")
    move_line_id = fields.Many2one('account.move.line', string="Invoice Line")
    member_type = fields.Selection(MEMBER_TYPE, string="Member Type")
    insurance_qualification = fields.Selection([
        ('cop', 'COP'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('advanced', 'Advanced Diploma'),
        ('other', 'Other'),
    ])
    sponsorship_type = fields.Selection([
        ('self', 'Self Sponsor'),
        ('company', 'Company Sponsor'),
    ])
    sponsor = fields.Many2one('res.partner', string="Sponsor")
    nationality = fields.Many2one('res.country', string="Nationality")
    personal_statement = fields.Binary(string="Personal Statement")
    state = fields.Selection(STATE, default='draft')
    gender = fields.Selection(GENDER, string="Gender")
    religion = fields.Selection(RELIGION, string='Religion')
    other_religion = fields.Char("Other Religion")

    company_name = fields.Char("Company Name")
    company_location = fields.Char("Company Location/Address")
    company_website = fields.Char("Company Website", required=False)
    organisation_type = fields.Selection(ORGAN_T, string="Organisation Type")
    company_ceo = fields.Char("Company CEO")
    company_ceo_tel = fields.Char("Company CEO Telephone")
    ceo_email = fields.Char("Company CEO Email")
    company_cordinator = fields.Char("Company Coordinator")
    company_cordinator_tel = fields.Char("Coordinator Telephone")
    company_cordinator_email = fields.Char("Coordinator Email")
    memorandum_assoc = fields.Binary(string="Memorandum & Articles")
    cert_incorp = fields.Binary(string="Certificate of Incorporation")
    other_info = fields.Char("Other")
    reject_reason = fields.Text("Reason")
    reg_invoice_state = fields.Char('Reg Invoice Status', size=20, readonly=True, compute='_compute_reg_invoice_state', store=False)
    invoice_status = fields.Char('Invoice Status', size=20, compute='_compute_invoiceStatus', default='NO INVOICE FOUND')


    institute_ids = fields.One2many('institute.record', 'application_id', string="University / College")
    employment_ids = fields.One2many('employment.record', 'application_id', string="Work Experience")
    other_professional_org_ids = fields.One2many('other.professional.organisation', 'application_id', string="Other Professional Organisations")
    other_informal_training_ids = fields.One2many('other.informal.training', 'application_id', string="Other Informal Training")


    
    position_held = fields.Char(string="Position Held")
    desc_duties = fields.Text(string="Description of duties and responsibilities:")
    # organisation_structure = fields.Binary(string="Organisational Structure")
    declaration = fields.Text(string="Declaration")
    member_proposer1 = fields.Many2one('res.partner', string='Proposers 1', no_create=True, domain=[('membership_state', '=', 'paid')])
    email_proposer1 = fields.Char(string="Email", related='member_proposer1.email')
    member_seconder1 = fields.Many2one('res.partner', string='Seconder 1', no_create=True, domain=[('membership_state', '=', 'paid')], unique=True )
    email_seconder1 = fields.Char(string="Email", related='member_seconder1.email')
    approval1_status = fields.Selection(APPROVAL, string="Approval Status")
    approval2_status = fields.Selection(APPROVAL, string="Approval Status")
    class_recommended = fields.Char(string="Class Recommended")
    cmtee_min = fields.Text(string="Cm'ttee Min")
    cmtee_remarks =fields.Text(string="Cm'ttee Remarks")    
    provisional_result = fields.Text(string="Provisional Result")
    date_assessed =fields.Date(string="Date Assessed")

    city = fields.Many2one('unamhe.cities', string='City')
    district = fields.Many2one('unamhe.district', string="District")
    personal_email = fields.Char(string="Personal Email :")
    mobile_no = fields.Char(string="Mobile No :")
    whatsapp_no = fields.Char(string="Whatsapp No :")
    post_addres = fields.Char(string='Postal Address')
    





    @api.model
    def create(self, vals):
        if vals['member_type'] == 'person':
            sequence = self.env['ir.sequence'].next_by_code('unamhe.membership.application')
            vals['name'] = sequence
        else:
            sequence = self.env['ir.sequence'].next_by_code('unamhe.membership.application.2')
            vals['name'] = sequence
        res = super(MembershipApplication, self).create(vals)
        return res

    def send_for_approval(self):
        if self.sponsorship_type == "company":
            self.write({'state': 'sponsor_review'})
        else:
            act = self.env['account.move'].search(
                [('memb_application_id', '=', self.id), ('amount_residual', '!=', 0), ('state', '!=', 'cancel'),
                 ('payment_state', '!=', 'paid')])
            if act:
                raise models.ValidationError(_("There are unpaid balances on this record"))
            self.write({'state': 'approve'})

    def send_email_wizard(self):
        self.ensure_one()
        # self.state = 'approve'
        template_id = self.env.ref('unamhe_membership.unamhe_member_application_rejected_email', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model="unamhe.membership.application",
            default_res_id=self.id,
            default_use_template=bool(template_id),
            default_template_id=template_id.id,
            default_composition_mode='comment',
            default_is_log=False,
            custom_layout='mail.mail_notification_light',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.depends('state')
    def _compute_reg_invoice_state(self):
        for record in self:
            state = 'no invoice'
            if record.user_id.partner_id and record.user_id.partner_id.id:
                # get registration invoice
                # reg_fee_inv_line_category = 'reg-%s-%s' % (record.course_id.id, record.batch_id.id)
                user_invoices = self.env['account.move'].search([('partner_id', '=', record.user_id.partner_id.id)])
                for inv in user_invoices:
                    for line in inv.invoice_line_ids:
                        if line.item_category == 'membership':
                            state = inv.payment_state
                            break
                record.reg_invoice_state = state

    def action_reject_application(self):
        self.write({'state': 'reject'})

        try:
            if self.sponsorship_type != 'company':
                invoice = self.env['account.move'].sudo().search([('memb_application_id', '=', self.id)])
                invoice.sudo().unlink()
        except Exception:
            pass

        # send email
        mail_template = self.env.ref('unamhe_membership.unamhe_member_application_rejected_email', raise_if_not_found=False)
        mail_template.sudo().send_mail(self.id, force_send=False)

    def _compute_invoiceStatus(self):
        for app in self:
            # check if invoices are paid
            if app.sponsorship_type == 'company':
                mv_id = self.env['account.move.line'].search([
                    ('partner_id', '=', app.sponsor.id),
                    ('for_partner_id', '=', app.user_id.partner_id.id),
                    ('memb_application_id', '=', app.id)])

                if len(mv_id) > 0:
                    for items in mv_id:
                        if items.move_id.payment_state != 'paid':
                            app.invoice_status = 'NOT PAID'
                        else:
                            app.invoice_status = 'PAID'
                else:
                    app.invoice_status = "NO INVOICE FOUND"

            else:
                invoice = self.env['account.move'].search([('memb_application_id', '=', app.id)])
                if invoice.payment_state != 'paid':
                    app.invoice_status = 'NOT PAID'
                else:
                    app.invoice_status = 'PAID'

    def application_approval(self):
        self.approval_date = datetime.datetime.now()
        self.write({'state': 'approved'})
        # send email
        mail_template = self.env.ref('unamhe_membership.unamhe_member_application_approved_email', raise_if_not_found=False)
        mail_template.sudo().send_mail(self.id, force_send=False)

    def approve_application_sponsor(self):
        act = self.env['account.move'].search(
            [('partner_id', '=', self.sponsor.name.id), ('amount_residual', '!=', 0), ('state', '!=', 'cancel'),
             ('payment_state', '!=', 'paid')])
        if act:
            raise models.ValidationError(_("There are unpaid balances on this record"))
        else:
            self.approval_date = datetime.datetime.now()
            self.write({'state': 'approved'})

    def back_btn(self):
        partner = self.user_id.partner_id
        partner_record = self.env['res.partner'].search([('id', '=', partner.id)])
        if partner_record.membership_state == 'paid':
            partner_record.membership_state = 'invoiced'
        self.write({'state': 'approved'})

    def unlink(self):
        for app in self:
            if app.state in ['approved', 'registered']:
                raise models.ValidationError(_("You cannot delete an already approved and registered application"))
        res = super(MembershipApplication, self).unlink()
        return res

    def register_member(self):
        if not self.user_id or not self.user_id.id:
            raise models.ValidationError(_("This member entry is invalid and cannot be registered because it does not have a linked user account"))

        # check if invoices are paid
        if self.sponsorship_type == 'company':
            mv_id = self.env['account.move.line'].search([
                ('partner_id', '=', self.sponsor.id),
                ('for_partner_id', '=', self.user_id.partner_id.id),
                ('memb_application_id', '=', self.id)])
            for items in mv_id:
                if items.move_id.state in ['posted'] and items.move_id.amount_residual != 0:
                    raise models.ValidationError(_("The Sponsor has not completed payment for this application"))
        else:
            act = self.env['account.move'].search(
                [('memb_application_id', '=', self.id), ('amount_residual', '!=', 0), ('state', '!=', 'cancel'),
                 ('payment_state', '!=', 'paid')])
            if act:
                raise models.ValidationError(_("There are unpaid balances on this record"))

        if self.member_type == 'person':
            # get next member ID
            member_id = self.env['membership.individual.id.gen'].sudo().create({'src': 'C'})

            values = {
                'member_type': self.member_type,
                'company_type': self.member_type,
                'membership_id': member_id.membership_id,
                'product': self.product.id,
                'date_of_birth': self.date_of_birth,
                'is_company': False,
                'phone': self.phone,
                'gender': self.gender,
                'mobile': self.mobile,
                'membership_state': 'paid',
                'image_1920': self.image_1920,
                'country_id': self.nationality,
                'member': True,
                # 'academic_documents': self.academic_documents,
                # 'other_academic_documents': self.other_academic_documents if self.other_academic_documents else False,
            }
            self.user_id.partner_id.write(values)

            # change login username to membership ID
            self.user_id.write({'login': member_id.membership_id})

        elif self.member_type == 'company':
            # get next member ID
            member_id = self.env['membership.corporate.id.gen'].sudo().create({'src': 'C'})

            values = {
                'member': True,
                'member_type': self.member_type,
                'company_type': self.member_type,
                'membership_id': member_id.membership_id,
                'product': self.corporate_product.id,
                'is_company': True,
                'organisation_type': self.organisation_type,
                'company_ceo': self.company_ceo,
                'company_ceo_tel': self.company_ceo_tel,
                'ceo_email': self.ceo_email,
                'company_cordinator': self.company_cordinator,
                'company_cordinator_tel': self.company_cordinator_tel,
                'company_cordinator_email': self.company_cordinator_email,
                'membership_state': 'paid',
            }
            self.user_id.partner_id.write(values)

            # change login username to membership ID
            self.user_id.write({'login': member_id.membership_id})
        else:
            raise models.ValidationError(_("You have no values"))

        self.write({'state': 'registered'})

        # send email
        # mail_template = self.env.ref('unamhe_membership.unamhe_member_application_notification_email', raise_if_not_found=False)
        # mail_template.sudo().send_mail(self.id, force_send=False)
        #
        mail_template = self.env.ref('unamhe_membership.unamhe_member_application_approved_email', raise_if_not_found=False)
        mail_template.sudo().send_mail(self.id, force_send=False)
class InstituteRecord(models.Model):
    _name = 'institute.record'
    _description = 'Institute Record for Course Application'

    application_id = fields.Many2one('unamhe.membership.application', string="Application", ondelete='cascade')
    name = fields.Char(string="Name of University / College")
    edu_starting_date = fields.Date(string="Starting Date")
    edu_ending_date = fields.Date(string="Ending Date")
    qualification = fields.Char(string="Award / Course Title")
    attachment_results = fields.Binary(string="Academic Attachment", attachment=True)

class EmploymentRecord(models.Model):
    _name = 'employment.record'
    _description = 'Employment Record for Course Application'

    application_id = fields.Many2one('unamhe.membership.application', string="Application", ondelete='cascade')
    employer_name = fields.Char(string="Oraganisation")
    work_starting_date = fields.Date(string="Starting Date")
    work_ending_date = fields.Date(string="Ending Date")
    desc_work = fields.Text(string="Description of work")
    nationality = fields.Many2one('res.country', string="Nationality")
    city_work = fields.Many2one('unamhe.cities', string='City')
    district_work = fields.Many2one('unamhe.district', string="District")
    date_assessed_work =fields.Date(string="Date Assessed")

class OtherProfessionalOrganisation(models.Model):
    _name = 'other.professional.organisation'
    _description = 'Other Professional Organisation'

    application_id = fields.Many2one('unamhe.membership.application', string="Application", ondelete='cascade')
    name = fields.Char(string="Name of Organisation", required=True)
    other_starting_date = fields.Date(string="Starting Date")
    other_ending_date = fields.Date(string="Ending Date")
    level_membership = fields.Char(string="Level of Membership")
    nationality_org = fields.Many2one('res.country', string="Nationality")
    cert_attached = fields.Binary(string='Certificate Attachment')
    abbr = fields.Char(string='Abbreviation')
    year_qualification = fields.Char(string='Year of 1st Qualification')

class OtherInformalTraining(models.Model):
    _name = 'other.informal.training'
    _description = 'Other Informal Training'

    application_id = fields.Many2one('unamhe.membership.application', string="Application", ondelete='cascade')
    informal_starting_date = fields.Date(string="Starting Date")
    informal_ending_date = fields.Date(string="Ending Date")
    training_details = fields.Text(string="Details of Training")
    employer_name = fields.Char(string="Name of Employer")
    post_held = fields.Char(string="Post Held")
    training_attachment = fields.Binary(string="Training Attachment", attachment=True)


class MemberApplicationRejectReason(models.TransientModel):
    _name = 'unamhe.membership.application.reject.reason'

    reason = fields.Text("Reason", required=True)
    application_id = fields.Many2one('unamhe.membership.application')

    def reject_application_with_reason(self):
        for rec in self:
            rec.application_id.update({
                'reject_reason': rec.reason
            })
            rec.application_id.action_reject_application()


class MembershipApplicationUpgrade(models.Model):
    _name = 'unamhe.membership.upgrade'
    _description = 'Membership Upgrade'
    _order = 'create_date DESC'

    MEMBER_TYPE = [
        ('person', 'Individual'),
        ('company', 'Corporate'),
    ]

    @api.model
    def _get_current_date(self):
        """ :return current date """
        return fields.Date.today()

    STATE = [
        ('draft', 'New Application'),
        ('approve', 'Submitted'),
        ('reject', 'Rejected'),
        ('approved', 'Approved'),
        ('upgraded', 'Upgraded'),
    ]

    SPON_TYPE = [
        ('self', 'Self Sponsor'),
        ('company', 'Company Sponsor'),
    ]
    admin = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    name = fields.Char("Number")
    member_name = fields.Char("Name", required=True)
    date = fields.Date("Date", default=lambda self: self._get_current_date())
    current_employer = fields.Char('Current Employer')
    current_position = fields.Char('Position At Work')
    employee_address = fields.Text("Postal Address of Employer")
    employement_history = fields.Text("Employment History")
    insurance_training = fields.Text("Insurance Training")
    events_attended = fields.Text("Major Events Attended")
    awards_received = fields.Text("Insurance Awards Received")
    other_qualification = fields.Char("Other Qualification")
    academic_documents = fields.Binary('Insurance Documents')
    other_academic_documents = fields.Binary(string="Other Qualifications", required=False)
    current_product = fields.Many2one('product.product', 'Current Membership', required=True)
    product = fields.Many2one('product.product', 'Upgrading to')
    member_type = fields.Selection(MEMBER_TYPE, string="Member Type")
    user_id = fields.Many2one('res.users', string="Users")
    sponsorship_type = fields.Selection(SPON_TYPE, required=True)
    sponsor = fields.Many2one('res.partner', string="Sponsor", required=False)
    personal_statement = fields.Binary(string="Personal Statement")
    reject_reason = fields.Text("Reason")
    state = fields.Selection(STATE, default='draft')
    invoice_status = fields.Char('Invoice Status', size=20, compute='_compute_invoiceStatus', default='NO INVOICE FOUND')
    admitted = fields.Selection(admin, string='Admitted')
    date_admitted = fields.Date(string='Date Admitted')
    council_min = fields.Text(string="Council Min")
    remarks = fields.Text(string='Remarks')

    def _compute_invoiceStatus(self):
        for app in self:
            # check if invoices are paid
            if app.sponsorship_type == 'company':
                mv_id = self.env['account.move.line'].search([
                    ('partner_id', '=', app.sponsor.id),
                    ('for_partner_id', '=', app.user_id.partner_id.id),
                    ('memb_upgrade_id', '=', app.id)])

                if len(mv_id) > 0:
                    for items in mv_id:
                        if items.move_id.payment_state != 'paid':
                            app.invoice_status = 'NOT PAID'
                        else:
                            app.invoice_status = 'PAID'

                else:
                    app.invoice_status = "NO INVOICE FOUND"
            else:
                invoice = self.env['account.move'].search([('memb_upgrade_id', '=', app.id)])
                if invoice.payment_state != 'paid':
                    app.invoice_status = 'NOT PAID'
                else:
                    app.invoice_status = 'PAID'

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('unamhe.membership.upgrade')
        vals['name'] = sequence
        res = super(MembershipApplicationUpgrade, self).create(vals)
        return res

    def submit_btn(self):
        self.write({'state': 'approve'})

    def action_reject_upgrade(self):
        self.write({'state': 'reject'})
        # send email
        mail_template = self.env.ref('unamhe_membership.unamhe_member_upgrade_rejected_email', raise_if_not_found=False)
        mail_template.sudo().send_mail(self.id, force_send=False)

    def approve_btn(self):
        if self.sponsorship_type == "company":
            self.write({'state': 'sponsor_review'})
        else:
            partner = self.user_id.partner_id
            lines = []
            inv_lines = {
                'product_id': self.product.id,
                'name': 'Membership Upgrade to ' + self.product.name,
                'quantity': 1,
                'tax_ids': self.product.taxes_id,
                'price_unit': self.product.list_price,
                'for_partner_id': partner.id,
                'memb_upgrade_id': self.id,
            }
            lines.append((0, 0, inv_lines))
            vals = {
                'partner_id': partner.id,
                'invoice_date': datetime.datetime.now(),
                'move_type': 'out_invoice',
                'memb_upgrade_id': self.id,
                'invoice_line_ids': lines,
            }
            voice = self.env['account.move'].sudo().create(vals).action_post()
            self.write({'state': 'approved'})

    def upgrade_btn(self):
        partner = self.user_id.partner_id
        if self.sponsorship_type == 'company':
            mv_id = self.env['account.move.line'].search([
                ('partner_id', '=', self.sponsor.id),
                ('for_partner_id', '=', partner.id),
                ('memb_upgrade_id', '=', self.id)])
            for items in mv_id:
                if items.move_id.state in ['posted'] and items.move_id.amount_residual != 0:
                    raise models.ValidationError(_("The Sponsor has not completed payment for this application"))
        else:
            act = self.env['account.move'].search(
                [('memb_upgrade_id', '=', self.id), ('amount_residual', '!=', 0), ('state', '!=', 'cancel'),
                 ('payment_state', '!=', 'paid')])
            if act:
                raise models.ValidationError(_("There are unpaid balances on this record"))

        values = {
            'product': self.product.id,
            'current_employer': self.current_employer,
            'current_position': self.current_position,
            'employee_address': self.employee_address,
            'employement_history': self.employement_history,
            'insurance_training': self.insurance_training,
            'events_attended': self.events_attended,
            'awards_received': self.awards_received,
            'personal_statement': self.personal_statement,
            'academic_documents': self.academic_documents,
            'other_academic_documents': self.other_academic_documents if self.other_academic_documents else False,
            'membership_state': 'paid'
        }
        partner.write(values)
        self.write({'state': 'upgraded'})

        # send email
        mail_template = self.env.ref('unamhe_membership.unamhe_member_upgrade_success_email', raise_if_not_found=False)
        mail_template.sudo().send_mail(self.id, force_send=False)

    def send_email_wizard(self):
        self.ensure_one()
        # self.state = 'approve'
        template_id = self.env.ref('unamhe_membership.unamhe_member_upgrade_rejected_email', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model="unamhe.membership.upgrade",
            default_res_id=self.id,
            default_use_template=bool(template_id),
            default_template_id=template_id.id,
            default_composition_mode='comment',
            default_is_log=False,
            custom_layout='mail.mail_notification_light',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


class MemberUpgradeRejectReason(models.TransientModel):
    _name = 'unamhe.membership.upgrade.reject.reason'

    reason = fields.Text("Reason", required=True)
    upgrade_id = fields.Many2one('unamhe.membership.upgrade')

    def reject_upgrade_with_reason(self):
        for rec in self:
            rec.upgrade_id.update({
                'reject_reason': rec.reason
            })
            rec.upgrade_id.action_reject_upgrade()


class MembershipRenewal(models.Model):
    _name = 'unamhe.membership.renewal'
    _description = 'Membership Renewal'
    _order = 'create_date DESC'
    _rec_name = "partner_id"

    SPON_TYPE = [
        ('self', 'Self Sponsor'),
        ('company', 'Company Sponsor'),
    ]
    STATE = [
        ('draft', 'New Application'),
        ('approve', 'Submitted'),
        ('sponsor_review', 'Sponsor Review'),
        ('sponsor_approve', 'Sponsor Approved'),
        ('sponsor_reject', 'Sponsor Rejected'),
        ('registered', 'Confirmed'),
    ]
    name = fields.Char("New")
    partner_id = fields.Many2one('res.partner', 'Member Name')
    sponsorship_type = fields.Selection(SPON_TYPE, string="Sponsorship Type")
    sponsor = fields.Many2one('res.partner', string="Sponsor")
    product = fields.Many2one('product.product', 'Membership Category')
    state = fields.Selection(STATE, default='draft')
    year = fields.Char('Year', required=True, size=20)
    invoice_status = fields.Char('Invoice Status', size=20, compute='_compute_invoiceStatus', default='NO INVOICE FOUND')

    def _compute_invoiceStatus(self):
        for app in self:
            # check if invoices are paid
            if app.sponsorship_type == 'company':
                mv_id = self.env['account.move.line'].search([
                    ('partner_id', '=', app.sponsor.id),
                    ('for_partner_id', '=', app.partner_id.id),
                    ('memb_renew_id', '=', app.id)])

                if len(mv_id) > 0:
                    for items in mv_id:
                        if items.move_id.payment_state != 'paid':
                            app.invoice_status = 'NOT PAID'
                        else:
                            app.invoice_status = 'PAID'
                else:
                    app.invoice_status = "NO INVOICE FOUND"

            else:
                invoice = self.env['account.move'].search([('memb_renew_id', '=', app.id)])
                if invoice.payment_state != 'paid':
                    app.invoice_status = 'NOT PAID'
                else:
                    app.invoice_status = 'PAID'

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('unamhe.membership.renewal')
        vals['name'] = sequence
        res = super(MembershipRenewal, self).create(vals)
        return res

    def approve_renawal(self):
        self.write({'state': 'approve'})

    def confirm_renawal(self):
        if self.sponsorship_type == 'company':
            line = self.env['account.move.line'].search([
                ('partner_id', '=', self.sponsor.id),
                ('for_partner_id', '=', self.partner_id.id),
                ('memb_renew_id', '=', self.id)])
            for items in line:
                if items.move_id.state in ['posted'] and items.move_id.amount_residual != 0:
                    raise models.ValidationError(_("The Sponsor has not completed payment for this application"))
        else:
            act = self.env['account.move'].search(
                [('memb_renew_id', '=', self.id), ('amount_residual', '!=', 0), ('state', '!=', 'cancel'),
                 ('payment_state', '!=', 'paid')])
            if act:
                raise models.ValidationError(_("There are unpaid balances on this record"))

        end_date = datetime.datetime(int(self.year), 12, 31).date()
        # start_date = datetime.datetime(int(self.year), 1, 1).date()
        self.partner_id.write({
            # 'membership_start': start_date,
            'membership_stop': end_date,
            'membership_state': 'paid',
        })
        self.write({'state': 'registered'})

        # send email
        mail_template = self.env.ref('unamhe_membership.unamhe_member_renewal_success_email', raise_if_not_found=False)
        mail_template.sudo().send_mail(self.id, force_send=False)


class AccountMove(models.Model):
    _inherit = 'account.move'

    memb_application_id = fields.Many2one('unamhe.membership.application')
    memb_upgrade_id = fields.Many2one('unamhe.membership.upgrade')
    memb_renew_id = fields.Many2one('unamhe.membership.renewal')
