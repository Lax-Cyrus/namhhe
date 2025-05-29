# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date
from odoo import api, fields, models, _


class CPDPointsRegister(models.Model):
    _name = 'cpd.point.register'
    _order = 'id DESC'
    _description = "CDP POINTS REGISTER"

    ACTIVITY_TYPE = [
        ('INTERNAL', 'INTERNAL'),
        ('EXTERNAL', 'EXTERNAL'),
    ]

    STATUS_TYPE = [
        ('APPROVED', 'APPROVED'),
        ('PENDING-APPROVAL', 'PENDING-APPROVAL'),
    ]

    member = fields.Many2one('res.partner', string='Member', domain="[('member', '=', True)]")
    activity_date = fields.Date(string="Activity Date", required=True)
    year = fields.Char(size=10, string="Year", required=False)
    activity = fields.Char(size=1000, string='Activity')
    activity_organiser = fields.Char(string='Activity Organiser', size=500)
    points_awarded = fields.Float(string='Points Awarded')
    activity_type = fields.Selection(ACTIVITY_TYPE, string="Activity Type")
    certificate = fields.Binary(string="Certificate of Attendance", required=False)
    unamhe_accredited = fields.Selection((('NO', 'NO'), ('YES', 'YES')))
    status = fields.Selection(STATUS_TYPE, string="Status", tracking=True)

    def action_approve_external_cpd_awards(self):
        for cpd in self:
            cpd.status = "APPROVED"

    @api.model
    def create(self, vals):
        cpd = super(CPDPointsRegister, self).create(vals)
        cpd.year = str(cpd.activity_date.year).replace(',', '')
        return cpd
