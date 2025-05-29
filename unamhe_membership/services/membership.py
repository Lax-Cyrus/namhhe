from odoo import models, fields, api, _
from datetime import datetime, date


class MembershipService(models.AbstractModel):
    _name = "unamhe.membership.renewal.service"
    _description = "MemberShip Service"

    def checkMemberShipStatus(self):
        mailing_list = []
        for member in self.env['res.partner'].sudo().search([('member', '=', True)]):
            if member.checkMemberRenewalStatus() != "INACTIVE" and member.membership_id and member.product:
                host_name = self.env['ir.config_parameter'].get_param('web.base.url')
                # generate email body.
                email_body = {
                    'subject': f'Notice:- {member.product.name} Renewal',
                    'headers': f'Notice:- Membership Renewal',
                    'email_to': member.email,
                    'body_html': f'Hello {member.name} - ({member.membership_id}),'
                                 f'<br/><br/>Your membership  at unamhe is due for renewal, please follow the link below to renew your membership.'
                                 f'<br/><br/><a target="_blank" href="{host_name}/unamhe/renew-membership/">Click to complete your Membership Renewal Process</a>'
                                 f'<br/><br/>Best regards,'
                                 f'<br/>--- unamhe Membership Department ---'
                                 f'<br/>'
                }
                mail = self.env['mail.mail'].sudo().create(email_body)
                mailing_list.append(mail.id)

        # send notices to members if there are any with expired membership
        if len(mailing_list) > 0:
            return self.env['mail.mail'].sudo().search([('id', 'in', mailing_list)]).send()

        return False

    # send 3 months notice membership notification
    def sendMonthNoticeNotification(self):
        host_name = self.env['ir.config_parameter'].get_param('web.base.url')

        if datetime.now().date().month in [10, 11, 12] and datetime.now().date().day in [1, 8, 17, 30]:
            mailing_list = []
            for member in self.env['res.partner'].sudo().search([('member', '=', True)]):
                # get next year member lines
                if member.checkMemberRenewalStatus() == "INACTIVE" and member.membership_id and member.product:
                    # generate email notice object.
                    email_body = {
                        'subject': f'Notice:- {member.product.name} Renewal',
                        'headers': f'Notice:- Membership Renewal',
                        'email_to': member.email,
                        'body_html': f'Hello {member.name} - ({member.membership_id}),'
                                     f'<br/><br/>Your membership  at unamhe is due for renewal, please follow the link below to renew your membership.'
                                     f'<br/><br/><a target="_blank" href="{host_name}/unamhe/renew-membership/">Click to complete your Membership Renewal Process</a>'
                                     f'<br/><br/>Best regards,'
                                     f'<br/>--- unamhe Membership Department ---'
                                     f'<br/>'
                    }
                    mail = self.env['mail.mail'].sudo().create(email_body)
                    mail['body_html'] = f"{mail['body_html']}<br/><br/> Regards <br/><br/>--- unamhe Membership Team ---"
                    mailing_list.append(mail.id)

            # send notices to members if there are any whose membership expires at the end of the month but hasn't yet been renewed
            if len(mailing_list) > 0:
                return self.env['mail.mail'].sudo().search([('id', 'in', mailing_list)]).send()

        return False

    def sendSponsorNotification(self):  # send notifications about pending applications approvals every 6 hours
        # course = self.env['op.admission'].sudo().search([('state', '=', 'new_cmp')])
        course_unit_list = self.env['op.subject.registration'].sudo().search([('state', 'in', ['new_cmp', 'updated_cmp'])])
        membership = self.env['unamhe.membership.application'].sudo().search([('state', '=', 'sponsor_review')])
        upgrade_membership = self.env['unamhe.membership.upgrade'].sudo().search([('state', '=', 'sponsor_review')])
        renew_membership = self.env['unamhe.membership.renewal'].sudo().search([('state', '=', 'sponsor_review')])

        # get unique sponsors
        sponsors = [sponsor.course_sponsor_id.id for sponsor in course]
        sponsors += [sponsor.course_sponsor_id.id for sponsor in course_unit_list]
        sponsors += [sponsor.sponsor.id for sponsor in membership]
        sponsors += [sponsor.sponsor.id for sponsor in upgrade_membership]
        sponsors += [sponsor.sponsor.id for sponsor in renew_membership]

        unique_sponsors = list(set(sponsors))

        generated_emails = []
        for sponsor in self.env['res.partner'].sudo().search([('id', 'in', unique_sponsors)]):
            # generate details and email object
            sponsor_data = {
                "sponsor_fullname": sponsor.name,
                "membership_id": sponsor.partner_id.membership_id if sponsor.partner_id.membership_id else '',
            }
            # generate details for courses
            application_details = []
            for course in self.env['op.admission'].sudo().search([('course_sponsor_id', '=', sponsor.id), ('state', '=', 'new_cmp')]):
                application_details.append({
                    "application_number": course.application_number,
                    "fullname": course.partner_id.name,
                    "membership_id": course.partner_id.membership_id if course.partner_id.membership_id else '',
                    "details": f'{course.course_id.name} - ({course.course_id.unamhe_code})',
                })

            for course in self.env['op.subject.registration'].sudo().search([('course_sponsor_id', '=', sponsor.id), ('state', 'in', ['new_cmp', 'updated_cmp'])]):
                application_details.append({
                    "application_number": course.name,
                    "fullname": course.student_id.partner_id.name,
                    "membership_id": course.student_id.partner_id.membership_id if course.student_id.partner_id.membership_id else '',
                    "details": f'{course.course_id.name} - ({course.course_id.unamhe_code})',
                })

            for app in self.env['unamhe.membership.application'].sudo().search([('sponsor', '=', sponsor.id), ('state', '=', 'sponsor_review')]):
                application_details.append({
                    "application_number": app.name,
                    "fullname": app.member_name,
                    "membership_id": app.user_id.partner_id.membership_id if app.user_id.partner_id.membership_id else '',
                    "details": f'Membership Application - ({app.product.name})',
                })

            for upgrade in self.env['unamhe.membership.upgrade'].sudo().search([('sponsor', '=', sponsor.id), ('state', '=', 'sponsor_review')]):
                application_details.append({
                    "application_number": upgrade.name,
                    "fullname": upgrade.member_name,
                    "membership_id": upgrade.user_id.partner_id.membership_id if upgrade.user_id.partner_id.membership_id else '',
                    "details": f'Membership Upgrade - ({upgrade.product.name})',
                })

            for renewal in self.env['unamhe.membership.renewal'].sudo().search([('sponsor', '=', sponsor.id), ('state', '=', 'sponsor_review')]):
                application_details.append({
                    "application_number": renewal.name,
                    "fullname": renewal.partner_id.name,
                    "membership_id": renewal.partner_id.membership_id if renewal.partner_id.membership_id else '',
                    "details": f'Membership Renewal - ({renewal.product.name})',
                })

            # generate email body
            sponsor_data['application_details'] = application_details
            email_temp = self.env['ir.ui.view'].sudo()._render_template(
                'unamhe_membership.unamhe_membership_sponsor_template_email', values=sponsor_data)

            # create email
            mail = self.env['mail.mail'].sudo().create({
                'subject': 'Notification:- Request for Sponsorship Approval - Membership and Academic Programs',
                'headers': 'Notification:- Request for Sponsorship Approval - Membership and Academic Programs',
                'email_to': sponsor.email,
                'body_html': email_temp
            })
            generated_emails.append(mail.id)

        if len(generated_emails) > 0:
            self.env['mail.mail'].sudo().search([('id', 'in', generated_emails)]).send()

        return True
