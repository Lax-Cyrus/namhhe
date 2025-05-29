# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, date


class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_draft(self):
        # OVERRIDE to update the cancel date.
        res = super(AccountMove, self).button_draft()
        for move in self:
            if move.move_type == 'out_invoice':
                self.env['membership.membership_line'].search([
                    ('account_invoice_line', 'in', move.mapped('invoice_line_ids').ids)
                ]).write({'date_cancel': False})
        return res

    def button_cancel(self):
        # OVERRIDE to update the cancel date.
        res = super(AccountMove, self).button_cancel()
        for move in self:
            if move.move_type == 'out_invoice':
                self.env['membership.membership_line'].search([
                    ('account_invoice_line', 'in', move.mapped('invoice_line_ids').ids)
                ]).write({'date_cancel': fields.Date.today()})
        return res

    def write(self, vals):
        # OVERRIDE
        move = super(AccountMove, self).write(vals)

        for _move in self:
            lines_to_process = [line for line in _move.invoice_line_ids if line.product_id.membership and not line.line_status] if _move.move_type == 'out_invoice' and _move.payment_state == 'paid' else []

            # Nothing to process, break.
            if len(lines_to_process) > 0:
                memberships_vals = []
                invoice_lines = []
                for line in lines_to_process:
                    if line.memb_renew_id or line.memb_upgrade_id or line.memb_application_id or line.item_category == 'membership':
                        date_from = datetime(year=datetime.utcnow().year, month=1, day=1).date()
                        date_to = datetime(year=datetime.utcnow().year, month=12, day=31).date()

                        membership_val = {
                            'partner': line.for_partner_id.id,
                            'membership_id': line.product_id.id,
                            'member_price': line.price_unit,
                            'date': datetime.utcnow().date(),
                            'account_invoice_line': line.id,
                            'membership_code': line.product_id.product_tmpl_id.membership_code,
                            'membership_ranking': line.product_id.product_tmpl_id.membership_ranking,
                            'member_type': line.product_id.product_tmpl_id.membership_member_type,
                            'cpd_year': datetime.utcnow().year,
                            'min_cpd_points': line.product_id.product_tmpl_id.membership_min_cpd_points,
                        }

                        if line.memb_renew_id and line.memb_renew_id.id:
                            end_date = datetime(int(line.memb_renew_id.year), 12, 31).date()
                            start_date = datetime(int(line.memb_renew_id.year), 1, 1).date()
                            line.for_partner_id.write({
                                # 'membership_start': start_date,
                                'membership_stop': end_date,
                                'membership_state': 'paid',
                            })
                            membership_val['date_from'] = start_date
                            membership_val['date_to'] = end_date
                            memberships_vals.append(membership_val)
                            invoice_lines.append(line.id)
                        elif line.memb_upgrade_id and line.memb_upgrade_id.id:
                            today = datetime.utcnow().date()
                            membership_years = [int(y.date_to.year) for y in line.for_partner_id.member_lines if
                                                y.date_to.year >= today.year and
                                                y.membership_id.id == line.memb_upgrade_id.current_product.id]

                            year = max(membership_years) if len(membership_years) > 0 else today.year
                            end_date = datetime(int(year), 12, 31).date()
                            line.for_partner_id.write({
                                'membership_start': today,
                                'membership_stop': end_date,
                                'membership_state': 'paid',
                            })
                            membership_val['date_from'] = today
                            membership_val['date_to'] = end_date
                            memberships_vals.append(membership_val)
                            invoice_lines.append(line.id)
                        elif line.memb_application_id and line.memb_application_id.id:
                            membership_val['date_from'] = date_from
                            membership_val['date_to'] = date_to
                            memberships_vals.append(membership_val)
                            invoice_lines.append(line.id)
                        elif line.item_category == 'membership':
                            membership_val['date_from'] = date_from
                            membership_val['date_to'] = date_to
                            memberships_vals.append(membership_val)
                            invoice_lines.append(line.id)
                if len(memberships_vals) > 0:
                    self.env['membership.membership_line'].create(memberships_vals)

                if len(invoice_lines) > 0:
                    # update line status
                    for line in _move.invoice_line_ids:
                        if line.id in invoice_lines:
                            line.write({'line_status': True})
        return move


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    memb_application_id = fields.Many2one('unamhe.membership.application', required=False)
    memb_upgrade_id = fields.Many2one('unamhe.membership.upgrade', required=False)
    memb_renew_id = fields.Many2one('unamhe.membership.renewal', required=False)
    line_status = fields.Boolean(default=False)
    item_category = fields.Char(string='Item Category', size=15, index=True)
    for_partner_id = fields.Many2one('res.partner', 'Linked/For Partner')

    def write(self, vals):
        # OVERRIDE
        line = super(AccountMoveLine, self).write(vals)
        return line

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        lines = super(AccountMoveLine, self).create(vals_list)
        return lines
