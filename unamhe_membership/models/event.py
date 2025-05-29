# -*- coding: utf-8 -*-
# Author: brian.muhumuza@gmail.com
# Function: Add CPD fields to events
from odoo import api, fields, models, _
from odoo.http import request


class EventTemplateTicket(models.Model):
    _inherit = 'event.type.ticket'

    cpd_points = fields.Integer(string='CPD Points', default=0)
    discount_members = fields.Float("Member Discount (%)")
    price = fields.Float(string='Price', compute='_compute_price', digits='Product Price', readonly=False, store=True)

    @api.depends('product_id', 'discount_members')
    def _compute_price(self):
        for ticket in self:
            if ticket.product_id and ticket.product_id.lst_price:
                if ticket.product_id.lst_price > 0:
                    if ticket.discount_members > 0:
                        ticket.price = ticket.product_id.lst_price * ((100-ticket.discount_members)/100)
                    else:
                        ticket.price = ticket.product_id.lst_price
                else:
                    ticket.price = 0
            elif not ticket.price:
                ticket.price = 0


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    cpd_points = fields.Integer(string='CPD Points Received', default=0)

    def action_set_done(self):
        """ Close Registration """
        res = super(EventRegistration, self).action_set_done()
        for event in self:
            event.action_internal_cpd_awards()

    def action_internal_cpd_awards(self):
        for cpd in self:
            details = f'\n {cpd.event_ticket_id.name} - {cpd.event_ticket_id.cpd_points} Points'
            points = cpd.event_ticket_id.cpd_points
            obj = {
                'member': cpd.partner_id.id,
                'activity_date': cpd.event_id.date_begin,
                'activity': f'{cpd.event_id.name}: {details}',
                'activity_organiser': 'unamhe',
                'points_awarded': points,
                'unamhe_accredited': 'YES',
                'activity_type': 'INTERNAL',
                'status': 'APPROVED'
            }
            request.env['cpd.point.register'].create(obj)
            cpd.state = "done"


class unamheEvents(models.Model):
    _inherit = 'event.event'
    _description = 'Events'

    EVENT_CATEGORY = [
        ('PUBLIC', 'PUBLIC EVENT'),
        ('MEMBERS-ONLY', 'MEMBERS ONLY EVENT'),
    ]

    event_category = fields.Selection(EVENT_CATEGORY, string="Event Category", default="PUBLIC", required=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        user = self.env.user

        # Check if portal user and  membership status ==> INACTIVE, return only partner records
        # Add custom search behavior here
        # Modify the `args` parameter to add or remove search conditions
        # Call the original search method with super() and return the results
        if self._get_portal_group_id() in [group.id for group in user.groups_id] and user.partner_id.checkMemberStatus() == "INACTIVE":
            category_arg = ('event_category', 'in', ['PUBLIC'])
            args.append(category_arg)

        return super(unamheEvents, self).search(args, offset=offset, limit=limit, order=order)

    def _get_portal_group_id(self):
        Group = self.env['res.groups'].sudo()
        domain = [('name', '=', 'Portal')]
        groups = Group.search_read(domain, ['id'])
        return groups[0]['id']
