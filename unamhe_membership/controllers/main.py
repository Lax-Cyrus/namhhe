# -*- coding: utf-8 -*-
import logging
import base64
import re
from odoo import http
from odoo.http import content_disposition
from odoo.http import request
from datetime import datetime
from odoo import _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import datetime


class CustomerPortalPendingApprovals(CustomerPortal):
    # Preparing Menu an counter values
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user = request.env.user        
        
        # CPD points counter
        cpd_counter = request.env['cpd.point.register'].sudo().search_count([('member', '=', user.partner_id.id)])
        values['cpd_points'] = cpd_counter
        
        # member events counter
        now = datetime.utcnow()
        events_counter = request.env['event.event'].sudo().search_count([('stage_id', 'not in', [3,4]), ('date_begin', '>=', now)])
        values['member_events'] = events_counter
        return values


class MembershipRegistration(http.Controller):

    def get_member(self, partner_id=None, **kw):
        partner = request.env.user.partner_id
        member_obj = request.env['res.partner']
        if not partner_id:
            member = member_obj.sudo().search([
                ('id', '=', partner.id)])
        else:
            member = member_obj.sudo().browse(id)

            # access_role = self.check_access_role(student)
            # if not access_role:
            #     return False

        return member

    @http.route('/unamhe/member-application', type="http", auth="user", website=True)
    def AdmissionsMemberApplication(self, partner_id=None):
        member_data = self.get_member(partner_id=partner_id)
        product_individual = request.env['product.product'].sudo().search([('membership_member_type', '=', 'individual')], order="id desc")
        product_corporate = request.env['product.product'].sudo().search([('membership_member_type', '=', 'corporate')], order="id desc")
        sponsor = request.env['res.partner'].sudo().search([('member', '=', True), ('company_type', '=', 'company'),  ('is_company', '=', True)])
        nationality = request.env['res.country'].sudo().search([])
        city = request.env['unamhe.cities'].sudo().search([])
        district = request.env['unamhe.district'].sudo().search([])
        proposers_individual = request.env['res.partner'].sudo().search([('membership_state', '=', 'paid')])
        seconder1 = request.env['res.partner'].sudo().search([('membership_state', '=', 'paid')])
        # member = member_data.membership_id
        member = request.env['unamhe.membership.application'].sudo().search([('member_name','=',member_data.name), ('state', 'in', ('draft','approve','sponsor_review'))])
        if not member:
            return request.render('unamhe_membership.unamhe_membership_form', {
                'product_individual': product_individual,
                'product_corporate': product_corporate,
                'sponsor': sponsor,
                'nationality': nationality,
                'city': city,
                'district' : district,
                'username': member_data.name,
                'email': member_data.email,
                'member_proposer1_individual': proposers_individual,
                'member_seconder1_individual': seconder1,
            })
        else:
            return request.redirect('/unamhe/personal-profile')

    @http.route('/unamhe/registration-success', type="http", auth="user", website=True)
    def MembershipSuccessPage(self, partner_id=None, **kw):
        member_data = self.get_member(partner_id=partner_id)
        user = request.env.user
        image_file = kw.get('image_1920')        
        memorandum_assoc_file = kw.get('memorandum_assoc')
        cert_incorp_file = kw.get('cert_incorp')
        # organisation_structure_file = kw.get('organisation_structure')

        if kw.get('member_type') == 'person':
            product = request.env['product.product'].sudo().search([('id', '=', kw.get('product'))], limit=1)

            image_base64 = base64.b64encode(image_file.read()) if image_file else False
            # organisation_structure_base64 = base64.b64encode(organisation_structure_file.read()) if organisation_structure_file else False
            

            member = request.env['unamhe.membership.application'].sudo().create({
                'member_name': kw.get('member_name'),
                'member_type': kw.get('member_type'),
                'date_of_birth': kw.get('date_of_birth'),
                'phone': kw.get('phone'),
                'mobile': kw.get('mobile'),
                'email': kw.get('email'),
                'mobile_no' : kw.get('mobile_no'),
                'whatsapp_no' : kw.get('whatsapp_no'),
                'post_addres' : kw.get('post_addres'),
                'level_membership': kw.get('level_membership'),
                'home_address': kw.get('home_address'),
                'product': kw.get('product'),
                'public_service_grade': kw.get('public_service_grade'),
                'home_email': kw.get('home_email'),
                'nationality': kw.get('nationality'),
                'city' : kw.get('city'),
                'district' : kw.get('district'),
                'district_work' : kw.get('district_work'),
                'city_work' : kw.get('city_work'),
                'date_assessed' : kw.get('date_assessed'),
                'sponsorship_type': kw.get('sponsorship_type'),
                'home_mobile': kw.get('home_mobile'),
                'declaration': kw.get('declaration'),
                'user_id': user.id,
                'image_1920': image_base64,
                'position_held': kw.get('position_held'),
                'desc_duties': kw.get('desc_duties'),
                # 'organisation_structure': organisation_structure_base64,
                'member_proposer1': kw.get('member_proposer1'),
                'member_seconder1': kw.get('member_seconder1'),
                'institute_ids': kw.get('institute_ids'),
                'employment_ids': kw.get('employment_ids'),
                'other_professional_org_ids': kw.get('other_professional_org_ids'),
                'other_informal_training_ids': kw.get('other_informal_training_ids'),
            })

            # Process education records (using getlist for multiple entries)
            institute_names = request.httprequest.form.getlist('name_institute[]')
            institute_start_dates = request.httprequest.form.getlist('edu_starting_date[]')
            institute_end_dates = request.httprequest.form.getlist('edu_ending_date[]')
            institute_qualifications = request.httprequest.form.getlist('qualification[]')
            attachment_result = request.httprequest.files.getlist('attachment_results[]')

            for name, start_date, end_date, qualification, results in zip(institute_names, institute_start_dates, institute_end_dates, institute_qualifications, attachment_result):
                results_base64 = base64.b64encode(results.read()) if results else False
                request.env['institute.record'].sudo().create({
                    'application_id': member.id,  
                    'name': name,
                    'edu_starting_date': start_date,
                    'edu_ending_date': end_date,
                    'qualification': qualification,
                    'attachment_results': results_base64
                })

            # Process employment records (same approach)
            employer_names = request.httprequest.form.getlist('employer_name[]')
            work_start_dates = request.httprequest.form.getlist('work_starting_date[]')  
            work_end_dates = request.httprequest.form.getlist('work_ending_date[]')      
            descriptions = request.httprequest.form.getlist('desc_work[]')

            for employer, start_date, end_date, description in zip(employer_names, work_start_dates, work_end_dates, descriptions):
                request.env['employment.record'].sudo().create({
                    'application_id': member.id,  
                    'employer_name': employer,
                    'work_starting_date': start_date,
                    'work_ending_date': end_date,
                    'desc_work': description,
                })

            # Process professional organization records
            org_names = request.httprequest.form.getlist('org_name[]')
            org_start_dates = request.httprequest.form.getlist('org_start_date[]')
            org_end_dates = request.httprequest.form.getlist('org_end_date[]')
            org_levels = request.httprequest.form.getlist('org_level[]')
            cert_attachment = request.httprequest.files.getlist('cert_attached[]')
            org_abbr = request.httprequest.form.getlist('abbr[]')
            org_year_qualification = request.httprequest.form.getlist('year_qualification[]')

            for name, start_date, end_date, level, certificate, abbriviation, year in zip(org_names, org_start_dates, org_end_dates, org_levels, cert_attachment, org_abbr, org_year_qualification):
                certificate_base64 = base64.b64encode(certificate.read()) if certificate else False
                request.env['other.professional.organisation'].sudo().create({
                    'application_id': member.id,
                    'name': name,
                    'other_starting_date': start_date,
                    'other_ending_date': end_date,
                    'level_membership': level,
                    'abbr' : abbriviation,
                    'year_qualification' : year,
                    'cert_attached': certificate_base64
                    
                })

            # Process informal training records
            training_start_dates = request.httprequest.form.getlist('informal_start_date[]')
            training_end_dates = request.httprequest.form.getlist('informal_end_date[]')
            training_details = request.httprequest.form.getlist('training_details[]')
            training_employers = request.httprequest.form.getlist('employer_name_informal[]')
            training_posts = request.httprequest.form.getlist('post_held[]')
            training_attachments = request.httprequest.files.getlist('training_attachment[]')

            for start_date, end_date, details, employer, post, attachment in zip(training_start_dates, training_end_dates, training_details, training_employers, training_posts, training_attachments):
                attachment_base64 = base64.b64encode(attachment.read()) if attachment else False

                request.env['other.informal.training'].sudo().create({
                    'application_id': member.id,
                    'informal_starting_date': start_date,
                    'informal_ending_date': end_date,
                    'training_details': details,
                    'employer_name': employer,
                    'post_held': post,
                    'training_attachment': attachment_base64
                })

            # Handle invoice creation for self-sponsorship
            if kw.get('sponsorship_type') == 'self':
                product = request.env['product.product'].sudo().search([('id', '=', kw.get('product'))], limit=1)
                lines = []
                inv_lines = {
                    'product_id': product.id,
                    'quantity': 1,
                    'price_unit': product.list_price,
                    'tax_ids': product.taxes_id,
                    'for_partner_id': member_data.id,
                    'item_category': 'membership',
                    'memb_application_id': member.id
                }
                lines.append((0, 0, inv_lines))
                vals = {
                    'partner_id': member_data.id,
                    'invoice_date': datetime.now(),
                    'move_type': 'out_invoice',
                    'invoice_line_ids': lines,
                    'memb_application_id': member.id
                }
                invoice = request.env['account.move'].sudo().create(vals).action_post()
            else:
                # Handle sponsorship details if applicable
                values.update({
                    'sponsor': kw.get('sponsor'),
                })

                

                
                                
               
        else:
            memorandum_assoc = base64.b64encode(memorandum_assoc_file.read()) if memorandum_assoc_file else False
            cert_incorp = base64.b64encode(cert_incorp_file.read()) if cert_incorp_file else False

            product_corp = request.env['product.product'].sudo().search([('id', '=', kw.get('corporate_product'))], limit=1)
            corporate = {
                # 'member_name': kw.get('member_name'),
                'member_type': kw.get('member_type'),
                'company_name': kw.get('company_name'),
                'organisation_type': kw.get('organisation_type'),
                'company_location': kw.get('company_location'),
                'company_website': kw.get('company_website'),
                'company_ceo': kw.get('company_ceo'),
                'company_ceo_tel': kw.get('company_ceo_tel'),
                'ceo_email': kw.get('ceo_email'),
                'company_cordinator': kw.get('company_cordinator'),
                'company_cordinator_tel': kw.get('company_cordinator_tel'),
                'company_cordinator_email': kw.get('company_cordinator_email'),
                'corporate_product': kw.get('corporate_product'),
                'product': None,
                'user_id': user.id,
                'memorandum_assoc': memorandum_assoc,
                'cert_incorp': cert_incorp
            }
            member = request.env['unamhe.membership.application'].sudo().create(corporate)

            lines = []
            inv_lines = {
                'product_id': product_corp.id,
                'quantity': 1,
                'price_unit': product_corp.list_price,
                'tax_ids': product_corp.taxes_id,
                'for_partner_id': member_data.id,
                'item_category': 'membership',
                'memb_application_id': member.id
            }
            lines.append((0, 0, inv_lines))
            vals = {
                'partner_id': member_data.id,
                'invoice_date': datetime.now(),
                'move_type': 'out_invoice',
                'invoice_line_ids': lines,
                'memb_application_id': member.id
            }
            voice = request.env['account.move'].sudo().create(vals).action_post()
        return request.render('unamhe_membership.membership_thanks', {})
    
    @http.route(['/approve_application/<int:application_id>/<string:approver>'], type='http', auth="user", website=True)
    def approve_application(self, application_id, approver, **kwargs):
        application = request.env['unamhe.membership.application'].browse(application_id)
        if application.exists():
            application.record_feedback(approver, 'approved')
        return request.render('unamhe_membership.approval_confirmation', {'status': 'approved'})

    @http.route(['/reject_application/<int:application_id>/<string:approver>'], type='http', auth="user", website=True)
    def reject_application(self, application_id, approver, **kwargs):
        application = request.env['unamhe.membership.application'].browse(application_id)
        if application.exists():
            application.record_feedback(approver, 'rejected')
        return request.render('unamhe_membership.approval_confirmation', {'status': 'rejected'})

    @http.route('/unamhe/sponsor-applications', type="http", auth="user", website=True)
    def SponsorApplications(self, **kw):
        user = request.env.user
        course = request.env['op.admission'].sudo().search([('course_sponsor_id', '=', user.partner_id.id), ('state', '=', 'new_cmp')])
        course_unit_list = request.env['op.subject.registration'].sudo().search([('course_sponsor_id', '=', user.partner_id.id), ('state', 'in', ['new_cmp', 'updated_cmp'])])
        membership = request.env['unamhe.membership.application'].sudo().search([('sponsor', '=', user.partner_id.id), ('state', '=', 'sponsor_review')])
        upgrade_membership = request.env['unamhe.membership.upgrade'].sudo().search([('sponsor', '=', user.partner_id.id), ('state', '=', 'sponsor_review')])
        renew_membership = request.env['unamhe.membership.renewal'].sudo().search([('sponsor', '=', user.partner_id.id), ('state', '=', 'sponsor_review')])

        # get membership product for ORDINARY membership
        member_product = None
        membership_product_tmpl = request.env['product.template'].sudo().search([('membership', '=', True), ('membership_code', '=', 'ORDINARY')], limit=1)
        if membership_product_tmpl and membership_product_tmpl.id:
            member_product = request.env['product.product'].sudo().search([('product_tmpl_id', '=', membership_product_tmpl.id)], limit=1)

        links = True if course or membership or upgrade_membership or renew_membership else False

        data = {
            'course_list': course,
            'course_unit_list': course_unit_list,
            'membership': membership,
            'member_product': member_product,
            'upgrade_membership': upgrade_membership,
            'renew_membership': renew_membership,
            'links': links
        }

        return request.render('unamhe_membership.sponsor_application_courses', data)

    @http.route('/unamhe/approve-applications/<object_ids>/', type="http", auth="user", website=True)
    def ApproveApplications(self, object_ids, **kw):
        user = request.env.user
        admissions = []
        admission_units = []
        memberships = []
        upgrades = []
        renewals = []
        for obj in object_ids.split('|'):
            if "course-" in obj:
                admissions.append(int(obj.replace('course-', '')))
            if "registration-" in obj:
                admission_units.append(int(obj.replace('registration-', '')))
            if "member-" in obj:
                memberships.append(int(obj.replace('member-', '')))
            if "upgrade-" in obj:
                upgrades.append(int(obj.replace('upgrade-', '')))
            if "renew-" in obj:
                renewals.append(int(obj.replace('renew-', '')))

        # mandatory fees
        sponsor_invoice = None
        if len(memberships) > 0 or len(upgrades) > 0 or len(renewals) > 0:
            sponsor_invoice = request.env['account.move'].sudo().create({
                'partner_id': user.partner_id.id,
                'move_type': 'out_invoice',
            })

        # Approve admission applications
        mailing_list = []
        if len(admissions) > 0:
            mailing_list += self.ApproveAdmissionApplications(admissions, sponsor_invoice)

        if len(admission_units) > 0:
            mailing_list += self.ApproveAdmissionUnitsUpdates(admission_units, sponsor_invoice)

        # approve unamhe.membership.application
        if len(memberships) > 0:
            mailing_list += self.ApproveMembershipApplications(memberships, sponsor_invoice, 'application', 'memb_application_id')

        # approve unamhe.membership.upgrade
        if len(upgrades) > 0:
            mailing_list += self.ApproveMembershipApplications(upgrades, sponsor_invoice, 'upgrade', 'memb_upgrade_id')

        # approve unamhe.membership.renewal
        if len(renewals) > 0:
            mailing_list += self.ApproveMembershipApplications(renewals, sponsor_invoice, 'renewal', 'memb_renew_id')

        if sponsor_invoice:
            sponsor_invoice.action_post()

        if len(mailing_list) > 0:
            request.env['mail.mail'].sudo().search([('id', 'in', mailing_list)]).send()

        return request.redirect('/unamhe/sponsor-applications')

    def ApproveAdmissionUnitsUpdates(self, object_ids, invoice):
        kw = self
        user = request.env.user
        sponsor_admission = request.env['op.subject.registration'].sudo().search([('id', 'in', object_ids)])
        sponsor_admission.write({'state': 'cmp_approved'})
        mailing_list = []
        for obj in sponsor_admission:
            if obj.student_id.partner_id.email:
                mail = request.env['mail.mail'].sudo().create({
                    'subject': 'Notification:- Sponsorship Application Approved',
                    'headers': 'Notification:- Sponsorship Application Approved',
                    'email_to': obj.student_id.partner_id.email,
                    'body_html': f'Dear {obj.student_id.partner_id.name} <br/><br/>Your application for Sponsorship ({obj.course_id.name} - {obj.batch_id.name} Intake) has been approved by your sponsor {user.partner_id.name}<br/><br/> -- unamhe Admissions Team --'
                })
                mailing_list.append(mail.id)

        return mailing_list

    def ApproveAdmissionApplications(self, object_ids, invoice):
        kw = self
        user = request.env.user
        sponsor_admission = request.env['op.admission'].sudo().search([('id', 'in', object_ids)])
        sponsor_admission.write({'state': 'cmp_approved'})
        mailing_list = []
        for obj in sponsor_admission:
            if obj.partner_id.email:
                mail = request.env['mail.mail'].sudo().create({
                    'subject': 'Notification:- Sponsorship Application Approved',
                    'headers': 'Notification:- Sponsorship Application Approved',
                    'email_to': obj.partner_id.email,
                    'body_html': f'Your application for Sponsorship ({obj.course_id.name} - {obj.batch_id.name} Intake) has been approved by your sponsor {user.partner_id.name}<br/><br/> -- unamhe Admissions Team --'
                })
                mailing_list.append(mail.id)
        return mailing_list

    def ApproveMembershipApplications(self, object_ids, invoice, modal, custom_field):
        kw = self
        user = request.env.user
        membership_applications = request.env[f'unamhe.membership.{modal}'].sudo().search([('id', 'in', object_ids)])
        membership_applications.write({'state': 'sponsor_approve'})
        mailing_list = []
        # mandatory fees
        mandatory_fees_invoice = invoice
        for membership in membership_applications:
            inv_line = {
                'partner_id': user.partner_id.id,
                'product_id': membership.product.id,
                'tax_ids': membership.product.taxes_id,
                'quantity': 1,
                'name': f"{membership.product.name} for: \n"
                        f"{membership.user_id.partner_id.name if modal != 'renewal' else membership.partner_id.name} \n"
                        f"{membership.user_id.partner_id.email if modal != 'renewal' else membership.partner_id.name}",
                'price_unit': membership.product.list_price,
                'for_partner_id': membership.user_id.partner_id.id if modal != 'renewal' else membership.partner_id.id,
                custom_field: membership.id
            }
            mandatory_fees_invoice.sudo().write({'invoice_line_ids': [(0, 0, inv_line)]})
            membership.write({'state': 'sponsor_approve'})

            # add to sponsor profile
            sponsored = request.env['op.student.sponsors'].sudo().search([
                ('sponsor', '=', user.partner_id.id),
                ('student', '=', membership.user_id.partner_id.id if modal != 'renewal' else membership.partner_id.id)])
            if not sponsored:
                request.env['op.student.sponsors'].sudo().create(
                    {
                        'sponsor': user.partner_id.id,
                        'student': membership.user_id.partner_id.id if modal != 'renewal' else membership.partner_id.id,
                        'relationship': 'Sponsor'
                    })
            member_email = membership.user_id.partner_id.email if modal != 'renewal' else membership.partner_id.email
            if member_email:
                mail = request.env['mail.mail'].sudo().create({
                    'subject': 'Notification:- Sponsorship Application Approved',
                    'headers': 'Notification:- Sponsorship Application Approved',
                    'email_to': member_email,
                    'body_html': f'Your application for Sponsorship (membership {modal}) has been approved by your sponsor {user.partner_id.name}<br/><br/> -- unamhe Membership Team --'
                })
                mailing_list.append(mail.id)

        return mailing_list

    @http.route('/unamhe/reject-applications/<object_ids>/', type="http", auth="user", website=True)
    def RejectApplications(self, object_ids, **kw):
        user = request.env.user
        admissions = []
        admission_units = []
        memberships = []
        upgrades = []
        renewals = []
        for obj in object_ids.split('|'):
            if "course-" in obj:
                admissions.append(int(obj.replace('course-', '')))
            if "registration-" in obj:
                admission_units.append(int(obj.replace('registration-', '')))
            if "member-" in obj:
                memberships.append(int(obj.replace('member-', '')))
            if "upgrade-" in obj:
                upgrades.append(int(obj.replace('upgrade-', '')))
            if "renew-" in obj:
                renewals.append(int(obj.replace('renew-', '')))

        mailing_list = []

        # Approve admission applications
        if len(admissions) > 0:
            reject_admissions = request.env['op.admission'].sudo().search([('id', 'in', admissions)])
            reject_admissions.write({'state': 'cmp_rejected'})
            for obj in reject_admissions:
                if obj.partner_id.email:
                    mail = request.env['mail.mail'].sudo().create({
                        'subject': 'Notification:- Sponsorship Application Rejected',
                        'headers': 'Notification:- Sponsorship Application Rejected',
                        'email_to': obj.partner_id.email,
                        'body_html': f'Your application for Sponsorship ({obj.course_id.name} - {obj.batch_id.name} Intake) has been Rejected by your sponsor {user.partner_id.name}<br/><br/> -- unamhe Admissions Team --'
                    })
                    mailing_list.append(mail.id)

        # Approve admission units applications
        if len(admission_units) > 0:
            reject_admissions = request.env['op.subject.registration'].sudo().search([('id', 'in', admission_units)])
            reject_admissions.write({'state': 'cmp_rejected'})
            for obj in reject_admissions:
                if obj.student_id.partner_id.email:
                    mail = request.env['mail.mail'].sudo().create({
                        'subject': 'Notification:- Sponsorship Application Rejected',
                        'headers': 'Notification:- Sponsorship Application Rejected',
                        'email_to': obj.student_id.partner_id.email,
                        'body_html': f'Your application for Sponsorship ({obj.course_id.name} - {obj.batch_id.name} Intake) has been Rejected by your sponsor {user.partner_id.name} <br/><br/> -- unamhe Admissions Team --'
                    })
                    mailing_list.append(mail.id)

        # approve unamhe.membership.application
        if len(memberships) > 0:
            membership_application = request.env['unamhe.membership.application'].sudo().search([('id', 'in', memberships)])
            membership_application.write({'state': 'sponsor_reject'})
            for obj in membership_application:
                if obj.user_id.partner_id.email:
                    mail = request.env['mail.mail'].sudo().create({
                        'subject': 'Notification:- Sponsorship Application Rejected',
                        'headers': 'Notification:- Sponsorship Application Rejected',
                        'email_to': obj.user_id.partner_id.email,
                        'body_html': f'Your application for Sponsorship (membership) has been Rejected by your sponsor {user.partner_id.name}<br/><br/> -- unamhe Membeship Team --'
                    })
                    mailing_list.append(mail.id)

        # approve unamhe.membership.upgrade
        if len(upgrades) > 0:
            memberships_upgrades = request.env['unamhe.membership.upgrade'].sudo().search([('id', 'in', upgrades)])
            memberships_upgrades.write({'state': 'sponsor_reject'})
            for obj in memberships_upgrades:
                if obj.user_id.partner_id.email:
                    mail = request.env['mail.mail'].sudo().create({
                        'subject': 'Notification:- Sponsorship Application Rejected',
                        'headers': 'Notification:- Sponsorship Application Rejected',
                        'email_to': obj.user_id.partner_id.email,
                        'body_html': f'Your application for Sponsorship (membership upgrade) has been Rejected by your sponsor {user.partner_id.name}<br/><br/> -- unamhe Membeship Team --'
                    })
                    mailing_list.append(mail.id)

        # approve unamhe.membership.renewal
        if len(renewals) > 0:
            memberships_renewal = request.env['unamhe.membership.renewal'].sudo().search([('id', 'in', renewals)])
            memberships_renewal.write({'state': 'sponsor_reject'})
            for obj in memberships_renewal:
                if obj.user_id.partner_id.email:
                    mail = request.env['mail.mail'].sudo().create({
                        'subject': 'Notification:- Sponsorship Application Rejected',
                        'headers': 'Notification:- Sponsorship Application Rejected',
                        'email_to': obj.user_id.partner_id.email,
                        'body_html': f'Your application for Sponsorship (membership renewal) has been Rejected by your sponsor {user.partner_id.name}<br/><br/> -- unamhe Membeship Team --'
                    })
                    mailing_list.append(mail.id)

        request.env['mail.mail'].sudo().search([('id', 'in', mailing_list)]).send()

        return request.redirect('/unamhe/sponsor-applications')

    @http.route('/unamhe/cpd-points', type="http", auth="user", website=True)
    def CPDStatement(self, **kw):
        user = request.env.user
        cpd = request.env['cpd.point.register'].sudo().search([('member', '=', user.partner_id.id)])
        return request.render('unamhe_membership.member_cpd_statement', {'cpd_points': cpd})

    @http.route('/unamhe/cpd-external/register', type="http", auth="user", website=True)
    def ExternalCPDRegister(self, **kw):
        user = request.env.user
        current_year = datetime.now().year
        return request.render('unamhe_membership.external_cpd_registration_form_view', {'member': user, 'current_year': current_year})

    @http.route('/unamhe/external-cpd-registration', type="http",  auth="user", website=True)
    def ExternalCPDRegistration(self, **kw):
        user = request.env.user
        kw['member'] = user.partner_id.id
        kw['activity_type'] = 'EXTERNAL'
        kw['status'] = 'PENDING-APPROVAL'

        certificate = kw.get('certificate')
        if certificate:
            kw['certificate'] = base64.b64encode(certificate.read())
        else:
            kw['certificate'] = ''

        cpd = request.env['cpd.point.register'].sudo().create(kw)
        return request.redirect('/unamhe/cpd-points')

    @http.route('/my/cpd-report/<year>', type='http', auth='user', website=True)
    def download_cpd_report(self, year=None):
        user = request.env.user
        if not year:
            year = datetime.now().year

        cpd_data = request.env['cpd.point.register'].sudo().search([('year', '=', str(year).replace(',', '')), ('member', '=', user.partner_id.id)])
        data = {
            'cpd_lines': cpd_data,
            'cpd_year': str(year).replace(',', ''),
            'total_points_awarded': sum([cpd.points_awarded for cpd in cpd_data])
        }
        report = request.env.ref('unamhe_membership.unamhe_membership_cpd_report').with_user(SUPERUSER_ID)
        pdf = report.with_context(data)._render_qweb_pdf(set([user.partner_id.id]), data=data)[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', content_disposition(f"{user.partner_id.membership_id} CPD Certificate.pdf"))]
        return request.make_response(pdf, headers=pdfhttpheaders)
