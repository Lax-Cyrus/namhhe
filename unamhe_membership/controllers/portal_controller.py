import datetime
import base64
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo import http


class MembersPortal(CustomerPortal):

    # Preparing Menu an counter values
    def _prepare_home_portal_values(self, counters):
        rtn = super()._prepare_home_portal_values(counters)
        return rtn

    # Function to get the logged in user
    def get_member(self, partner_id=None):
        if partner_id:
            return request.env['res.partner'].sudo().browse(partner_id)
        else:
            return request.env['res.partner'].sudo().search([('id', '=', request.env.user.partner_id.id), ('membership_id', '!=', '')])

    @http.route(['/unamhe/member-events'], type="http", website=True)
    def MemberViewEvents(self):
        events = request.env['event.event'].sudo().search([('stage_id', '!=', 3 and 4)])
        return request.render('unamhe_membership.unamhe_member_event', {'events': events})

    @http.route(['/unamhe/personal-profile', '/unamhe/personal-profile/<int:partner_id>'], type='http', website=True)
    def MembershipProfilePage(self, partner_id=None):
        # if partner_id:
        partner = request.env.user.partner_id
        member_data = request.env['res.partner'].sudo().search([('id', '=', partner.id)])
        # member_data = self.get_member(partner_id=partner_id)
        if not member_data:
            return request.render('unamhe_membership.member_profile_form_view')
        if member_data.image_1920:
            member_img = member_data.image_1920.decode("utf-8")
        else:
            member_img = member_data.image_1920
        return request.render('unamhe_membership.member_profile_form_view', {
            'member': member_data,
            'member_img': member_img,
        })

    @http.route(['/unamhe/member-edit-profile', '/unamhe/member-edit-profile/<int:partner_id>'], type='http', website=True)
    def MembershipEditProfile(self, partner_id=None):
        # if partner_id:
        member_data = self.get_member(partner_id=partner_id)
        if not member_data:
            return request.render('unamhe_membership.my_members_page')

        if member_data.image_1920:
            member_img = member_data.image_1920.decode("utf-8")
        else:
            member_img = member_data.image_1920
        return request.render('unamhe_membership.member_edit_profile', {
            'member': member_data,
            'member_img': member_img,
        })

    @http.route(['/unamhe/edit-success'], type='http', website=True)
    def MembershipEditProfileSuccess(self, **kw):
        member_data = self.get_member()
        member_data.sudo().write(kw)
        return request.redirect('/unamhe/personal-profile')

    @http.route('/unamhe/upgrade-membership', auth="user", type="http", website=True)
    def membershipUpgrade(self, **kw):
        member_data = self.get_member()

        if member_data.product.associated_levels:
            next_products = [pd.associated_level for pd in member_data.product.associated_levels]
        else:
            product_individual = request.env['product.product'].sudo().search([('membership_member_type', '=', 'individual')])
            next_products = [pd for pd in product_individual if pd.membership_ranking == (member_data.product.membership_ranking - 1)]

        # sponsor = request.env['res.partner'].sudo().search([('member', '=', True), ('company_type', '=', 'company'),  ('is_company', '=', True)])
        sponsor = request.env['res.partner'].sudo().search([('company_type', '=', 'company'), ('is_company', '=', True)])
        return request.render('unamhe_membership.membership_upgrade_form_view', {
            'member': member_data,
            # 'product_individual': product_individual,
            'next_products': next_products,
            'sponsor': sponsor
        })

    @http.route(['/unamhe/renew-membership'], auth="user", type="http", website=True)
    def MemberRenew(self, **kw):
        member_data = self.get_member()

        current_year = datetime.datetime.now().year
        if member_data.checkMemberRenewalStatus() == 'INACTIVE':
            renewal_year = current_year
        else:
            renewal_year = member_data.membership_stop.year + 1

        # sponsor = request.env['res.partner'].sudo().search([('member', '=', True), ('company_type', '=', 'company'), ('is_company', '=', True)])
        sponsor = request.env['res.partner'].sudo().search([('company_type', '=', 'company'), ('is_company', '=', True)])
        return request.render("unamhe_membership.member_renew_template", {
            'member': member_data,
            'renewal_year': renewal_year,
            'sponsor': sponsor
        })

    @http.route('/unamhe/upgrade-membership-success', type="http", website=True)
    def MemberUpgradeSuccess(self, **kw):
        user = request.env.user
        member_data = self.get_member()

        academic_documents = kw.get('academic_documents')
        personal_statement = kw.get('personal_statement')
        other_academic_documents = kw.get('other_academic_documents')
        product = request.env['product.product'].sudo().search([('id', '=', kw.get('product'))], limit=1)

        academic_documents64 = base64.b64encode(academic_documents.read()) if kw.get('academic_documents') else False
        other_academic_documents64 = base64.b64encode(other_academic_documents.read()) if kw.get('other_academic_documents') else False
        personal_statement64 = base64.b64encode(personal_statement.read()) if kw.get('personal_statement') else False

        kw.update({'academic_documents': academic_documents64})
        kw.update({'other_academic_documents': other_academic_documents64})
        kw.update({'personal_statement': personal_statement64})
        kw.update({'user_id': user.id})

        if kw.get('sponsorship_type') == 'self':
            kw.update({'sponsor': None})

        upgrade = request.env['unamhe.membership.upgrade'].sudo().create(kw)
        return request.render('unamhe_membership.memberupgradesuccess', {})

    @http.route(['/unamhe/renew-membership-success'], auth="user", type="http", website=True)
    def renew_membership_success(self, **kw):
        member_data = self.get_member()
        product = request.env['product.product'].sudo().search([('id', '=', kw.get('product'))], limit=1)
        if member_data.member_type == 'person':
            if kw.get('sponsorship_type') == 'self':
                values = ({
                    'partner_id': member_data.id,
                    'sponsorship_type': kw.get('sponsorship_type'),
                    'product': kw.get('product'),
                    'sponsor': None,
                    'year': kw.get('year'),
                })
                renewal_id = request.env['unamhe.membership.renewal'].sudo().create(values)
                lines = []
                inv_lines = {
                    'product_id': product.id,
                    'quantity': 1,
                    'tax_ids': product.taxes_id,
                    'price_unit': product.list_price,
                    'for_partner_id': member_data.id,
                    'memb_renew_id': renewal_id.id,
                }
                lines.append((0, 0, inv_lines))
                vals = {
                    'partner_id': member_data.id,
                    'invoice_date': datetime.datetime.now(),
                    'move_type': 'out_invoice',
                    'memb_renew_id': renewal_id.id,
                    'invoice_line_ids': lines,
                }
                voice = request.env['account.move'].sudo().create(vals).action_post()
            elif kw.get('sponsorship_type') == 'company':
                values = ({
                    'partner_id': member_data.id,
                    'sponsorship_type': kw.get('sponsorship_type'),
                    'state': 'sponsor_review',
                    'year': kw.get('year'),
                    'product': kw.get('product'),
                    'sponsor': kw.get('sponsor')
                })
                renewal_id = request.env['unamhe.membership.renewal'].sudo().create(values)
        else:
            values = ({
                'partner_id': member_data.id,
                'product': kw.get('product'),
                'year': kw.get('year')
            })
            renewal_id = request.env['unamhe.membership.renewal'].sudo().create(values)
            lines = []
            inv_lines = {
                'product_id': product.id,
                'tax_ids': product.taxes_id,
                'name': "Corporate Renewal for" + product.name,
                'quantity': 1,
                'price_unit': product.list_price,
                'for_partner_id': member_data.id,
                'memb_renew_id': renewal_id.id,
            }
            lines.append((0, 0, inv_lines))
            vals = {
                'partner_id': member_data.id,
                'invoice_date': datetime.datetime.now(),
                'move_type': 'out_invoice',
                'memb_renew_id': renewal_id.id,
                'invoice_line_ids': lines,
            }
            voice = request.env['account.move'].sudo().create(vals).action_post()

        return request.render('unamhe_membership.memberupgradesuccess', {})

    @http.route('/my/members/', auth="user", type="http", website=True)
    def myMembers(self, **kw):
        user = request.env.user
        sponsored = request.env['op.student.sponsors'].sudo().search([('sponsor', '=', user.partner_id.id)])
        return request.render('unamhe_membership.my_sponsored_members_list', {'sponsored': sponsored})

    @http.route('/unamhe/sponsored-activities/<object_id>', auth="user", type="http", website=True)
    def sponsoredActivities(self, object_id):
        user = request.env.user
        sponsored_activities = request.env['account.move.line'].sudo().search([
            ('for_partner_id', '=', int(object_id)), ('partner_id', '=', user.partner_id.id), ('parent_state', '!=', 'draft')])
        data = {
            "member": request.env['res.partner'].sudo().search([('id', '=', int(object_id))]),
            "sponsored_activities": sponsored_activities
        }
        return request.render('unamhe_membership.my_sponsored_member_profile', data)

    # @http.route(['/unamhe/membership/applications'], type='http', csrf=False, website=True)
    # def member_application_list(self, **post):
    #     user = request.env.user
    #     sponsor = request.env['op.parent'].sudo().search([('name', '=', user.partner_id.id)], limit=1)
    #
    #     if sponsor and sponsor.id:
    #         applications = request.env['unamhe.membership.application'].sudo().search(
    #             [('sponsor', '=', sponsor.id), ('state', '=', 'sponsor_review')])
    #
    #         return request.render("unamhe_membership.sponsor_membership_applications",
    #                               {'applications': applications})
    #     else:
    #         return request.redirect('/my/home')

    # @http.route(['/unamhe/membership/upgrades'], type='http', csrf=False, website=True)
    # def member_upgrade_list(self, **post):
    #     user = request.env.user
    #     sponsor = request.env['op.parent'].sudo().search([('name', '=', user.partner_id.id)], limit=1)
    #     if sponsor and sponsor.id:
    #         upgrades = request.env['unamhe.membership.upgrade'].sudo().search(
    #             [('sponsor', '=', sponsor.id), ('state', '=', 'sponsor_review')])
    #
    #         return request.render("unamhe_membership.sponsor_membership_upgrades",
    #                               {'upgrades': upgrades})
    #     else:
    #         return request.redirect('/my/home')

    # @http.route(['/unamhe/membership/renew'], type='http', csrf=False, website=True)
    # def member_renew_list(self, **post):
    #     user = request.env.user
    #     sponsor = request.env['op.parent'].sudo().search([('name', '=', user.partner_id.id)], limit=1)
    #     if sponsor and sponsor.id:
    #         renewal = request.env['unamhe.membership.renewal'].sudo().search(
    #             [('sponsor', '=', sponsor.id), ('state', '=', 'sponsor_review')])
    #         # for items in renewal:
    #         return request.render("unamhe_membership.sponsor_membership_renewal",
    #                               {'renewal': renewal})
    #     else:
    #         return request.redirect('/my/home')

    # Controller to manage approvals By sponsors
    # @http.route('/unamhe/member-application/approve/', type='http', auth='public', website=True)
    # def admission_approve(self, **kw):
    #     user = request.env.user
    #     sponsor = request.env['op.parent'].sudo().search([('name', '=', user.partner_id.id)], limit=1)
    #     if sponsor and sponsor.id:
    #         partner = request.env['unamhe.membership.application'].sudo().search(
    #             [('id', '=', kw['id']), ('sponsor', '=', sponsor.id)], limit=1)
    #         related_partner = partner.user_id.partner_id.id
    #
    #         if partner and partner.id:
    #             lines = []
    #             inv_lines = {
    #                 'product_id': partner.product.id,
    #                 'quantity': 1,
    #                 'price_unit': partner.product.list_price,
    #                 'for_partner_id': related_partner,
    #                 'item_category': 'membership'
    #             }
    #             lines.append((0, 0, inv_lines))
    #             vals = {
    #                 'partner_id': sponsor.name.id,
    #                 'invoice_date': datetime.datetime.now(),
    #                 'move_type': 'out_invoice',
    #                 'memb_application_id': partner.id,
    #                 'invoice_line_ids': lines,
    #             }
    #             voice = request.env['account.move'].sudo().create(vals).action_post()
    #             partner.state = 'approved'
    #
    #         return request.redirect('/unamhe/membership/applications')
    #     else:
    #         return request.redirect('/my/home')

    # Controller to manage rejects By sponsors

    # @http.route('/unamhe/member-application/reject/', type='http', auth='public', website=True)
    # def member_application_reject(self, **kw):
    #     user = request.env.user
    #     sponsor = request.env['op.parent'].sudo().search([('name', '=', user.partner_id.id)], limit=1)
    #
    #     if sponsor and sponsor.id:
    #         partner = request.env['unamhe.membership.application'].sudo().search(
    #             [('id', '=', kw['id']), ('sponsor', '=', sponsor.id)], limit=1)
    #         if partner and partner.id and partner.membership_state == 'none':
    #             partner.sudo().write({'state': 'sponsor_reject'})
    #
    #         return request.redirect('/unamhe/membership/applications')
    #     else:
    #         return request.redirect('/my/home')
    #
    # @http.route('/unamhe/member-upgrade/approve/', type='http', auth='public', website=True)
    # def upgrade_approve(self, **kw):
    #
    #     user = request.env.user
    #     sponsor = request.env['op.parent'].sudo().search([('name', '=', user.partner_id.id)], limit=1)
    #
    #     if sponsor and sponsor.id:
    #         partner = request.env['unamhe.membership.upgrade'].sudo().search(
    #             [('id', '=', kw['id']), ('sponsor', '=', sponsor.id)], limit=1)
    #         related_partner = partner.user_id.partner_id.id
    #
    #         if partner and partner.id:
    #             lines = []
    #             inv_lines = {
    #                 'product_id': partner.product.id,
    #                 'quantity': 1,
    #                 'price_unit': partner.product.list_price,
    #                 'for_partner_id': related_partner,
    #                 'item_category': 'membership'
    #             }
    #             lines.append((0, 0, inv_lines))
    #             vals = {
    #                 'partner_id': sponsor.name.id,
    #                 'invoice_date': datetime.datetime.now(),
    #                 'move_type': 'out_invoice',
    #                 'memb_upgrade_id': partner.id,
    #                 'invoice_line_ids': lines,
    #             }
    #             voice = request.env['account.move'].sudo().create(vals).action_post()
    #             partner.state = 'approved'
    #
    #         return request.redirect('/unamhe/membership/upgrades')
    #     else:
    #         return request.redirect('/my/home')
    #
    # @http.route('/unamhe/member-upgrades/reject/', type='http', auth='public', website=True)
    # def member_upgrades_reject(self, **kw):
    #     user = request.env.user
    #     sponsor = request.env['op.parent'].sudo().search([('name', '=', user.partner_id.id)], limit=1)
    #
    #     if sponsor and sponsor.id:
    #         partner = request.env['unamhe.membership.upgrade'].sudo().search(
    #             [('id', '=', kw['id']), ('sponsor', '=', sponsor.id)], limit=1)
    #         if partner and partner.id and partner.membership_state == 'none':
    #             partner.sudo().write({'state': 'sponsor_reject'})
    #
    #         return request.redirect('/unamhe/membership/upgrades')
    #     else:
    #         return request.redirect('/my/home')
    #
    # @http.route('/unamhe/member-renew/approve/', type='http', auth='public', website=True)
    # def renew_approve(self, **kw):
    #
    #     user = request.env.user
    #     sponsor = request.env['op.parent'].sudo().search([('name', '=', user.partner_id.id)], limit=1)
    #
    #     if sponsor and sponsor.id:
    #         partner = request.env['unamhe.membership.renewal'].sudo().search(
    #             [('id', '=', kw['id']), ('sponsor', '=', sponsor.id)], limit=1)
    #         related_partner = partner.partner_id.id
    #         partner.state = 'sponsor_approved'
    #         if partner and partner.id:
    #             lines = []
    #             inv_lines = {
    #                 'product_id': partner.product.id,
    #                 'quantity': 1,
    #                 'price_unit': partner.product.list_price,
    #                 'for_partner_id': related_partner,
    #                 'item_category': 'membership'
    #             }
    #             lines.append((0, 0, inv_lines))
    #             vals = {
    #                 'partner_id': sponsor.name.id,
    #                 'invoice_date': datetime.datetime.now(),
    #                 'move_type': 'out_invoice',
    #                 'memb_renew_id': partner.id,
    #                 'invoice_line_ids': lines,
    #             }
    #             voice = request.env['account.move'].sudo().create(vals).action_post()
    #
    #         return request.redirect('/unamhe/membership/renew')
    #     else:
    #         return request.redirect('/my/home')
