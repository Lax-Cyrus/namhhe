# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models



class AccountMove(models.Model):
    _inherit = 'account.move'

    related_member = fields.Many2one('res.partner', string="Related Partner")


class Product(models.Model):
    _inherit = 'product.template'

    membership = fields.Boolean(help='Check if the product is eligible for membership.')
    membership_date_from = fields.Date(string='Membership Start Date',
        help='Date from which membership becomes active.')
    membership_date_to = fields.Date(string='Membership End Date',
        help='Date until which membership remains active.')
    # -- unamhe -- Membership fields
    membership_code = fields.Char(string='Membership Code', size=20)
    membership_ranking = fields.Integer(string='Membership Level Ranking', help='Ranking of the product. 1 = highest ranking level')
    membership_min_cpd_points = fields.Integer(string='Membership Mininum CPD Points', help='A member that does not attain the minimum CPD points should not be able to renew their membership')
    membership_member_type = fields.Selection(
        [('individual', 'Individual Members'), ('corporate', 'Corporate Members')], 'For Member Of Type'
    )

    associated_levels = fields.One2many('associated.products', 'membership', string='Associated Levels')

    _sql_constraints = [
        ('membership_date_greater', 'check(membership_date_to >= membership_date_from)', 'Error ! Ending Date cannot be set before Beginning Date.')
    ]

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if self._context.get('product') == 'membership_product':
            if view_type == 'form':
                view_id = self.env.ref('membership.membership_products_form').id
            else:
                view_id = self.env.ref('membership.membership_products_tree').id
        return super(Product, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)


class AssociatedProducts(models.Model):
    _name = 'associated.products'

    membership = fields.Many2one('product.template', string='Membership Level')
    associated_level = fields.Many2one('product.template', string='Associated Membership Level')

    _sql_constraints = [
        ('membership', 'check(membership == associated_levels)', 'Error ! Membership Level may not be same as Associated Membership Levels.')
    ]
