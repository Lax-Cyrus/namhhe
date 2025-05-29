# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, date

STATE = [
    ('none', 'Non Paid Member'),
    ('canceled', 'Cancelled Member'),
    ('inactive', 'Inactive Member'),
    ('expelled', 'Expelled Member'),
    ('blacklisted', 'Blacklisted Member'),
    ('old', 'Old Member'),
    ('waiting', 'Waiting Member'),
    ('invoiced', 'Invoiced Member'),
    ('free', 'Free Member'),
    ('paid', 'Paid Member'),
    ('active', 'Active Member')
]


class MembershipLine(models.Model):
    _name = 'membership.membership_line'
    _rec_name = 'partner'
    _order = 'id desc'
    _description = 'Membership Line'

    partner = fields.Many2one('res.partner', string='Partner', ondelete='cascade', index=True)
    membership_id = fields.Many2one('product.product', string="Membership", required=True)
    date_from = fields.Date(string='From', readonly=True)
    date_to = fields.Date(string='To', readonly=True)
    date_cancel = fields.Date(string='Cancel date')
    date = fields.Date(string='Join Date',
        help="Date on which member has joined the membership")
    member_price = fields.Float(string='Membership Fee',
        digits='Product Price', required=True,
        help='Amount for the membership')
    account_invoice_line = fields.Many2one('account.move.line', string='Account Invoice line', readonly=True, ondelete='cascade')
    account_invoice_id = fields.Many2one('account.move', related='account_invoice_line.move_id', string='Invoice', readonly=True)
    company_id = fields.Many2one('res.company', related='account_invoice_line.move_id.company_id', string="Company", readonly=True, store=True)
    state = fields.Selection(STATE, compute='_compute_state', string='Membership Status', store=True,
        help="It indicates the membership status.\n"
             "-Non Member: A member who has not applied for any membership.\n"
             "-Cancelled Member: A member who has cancelled his membership.\n"
             "-Old Member: A member whose membership date has expired.\n"
             "-Waiting Member: A member who has applied for the membership and whose invoice is going to be created.\n"
             "-Invoiced Member: A member whose invoice has been created.\n"
             "-Paid Member: A member who has paid the membership amount.")

    # -- unamhe fields --
    # Membership
    membership_code = fields.Char(string='Membership Code', size=20)
    membership_ranking = fields.Integer(string='Membership Level Ranking')
    member_type = fields.Char(string='Member Type', size=20)
    # CPD Reg --> individual members only
    cpd_year = fields.Integer(string='CPD Year', index=True)
    min_cpd_points = fields.Integer(string='Mininum Annual CPD Points')
    internal_points = fields.Integer(string='TT Internal CPD Points', default=0)
    external_points = fields.Integer(string='TT External CPD Points', default=0)
    total_points = fields.Integer(string='Total CPD Points', default=0)
    cpd_outcome = fields.Char(string='CPD Outcome', size=20)

    @api.depends('account_invoice_id.state',
                 'account_invoice_id.amount_residual',
                 'account_invoice_id.payment_state')
    def _compute_state(self):
        """Compute the state lines """
        if not self:
            return

        reverse_map = {}
        if len(tuple(self.mapped('account_invoice_id.id'))) > 0:
            self._cr.execute('''
                SELECT reversed_entry_id, COUNT(id)
                FROM account_move
                WHERE reversed_entry_id IN %s
                GROUP BY reversed_entry_id
            ''', [tuple(self.mapped('account_invoice_id.id'))])
            reverse_map = dict(self._cr.fetchall())

        partner_ids = []
        for line in self:
            partner_ids.append(line.partner.id)
            move_state = line.account_invoice_id.state
            payment_state = line.account_invoice_id.payment_state

            line.state = 'none'
            if move_state == 'draft':
                line.state = 'waiting'
            elif move_state == 'posted':
                if payment_state == 'paid':
                    if reverse_map.get(line.account_invoice_id.id):
                        line.state = 'canceled'
                    else:
                        line.state = 'paid'
                elif payment_state == 'in_payment':
                    line.state = 'paid'
                elif payment_state in ('not_paid', 'partial'):
                    line.state = 'invoiced'
            elif move_state == 'cancel':
                line.state = 'canceled'

        # force partner to recompute membership_state
        partner_model = self.env['res.partner']
        self.env.all.tocompute[partner_model._fields['membership_state']].update(partner_ids)
        partner_model.recompute()
    
    def scheduled_action_expire_old_membership(self, final=False):
        now = datetime.utcnow()
        first_year_day = date(year=now.year, month=1, day=1)

        expired = self.search([('state', 'in', ['invoiced','free','paid','active']), ('date_to', '<', first_year_day)])
        expired.write({'state': 'old'})