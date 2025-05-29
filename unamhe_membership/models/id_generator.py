# -*- coding: utf-8 -*-
# author: brian.muhumuza@gmail.com

from odoo import api, fields, models


class IndividualIdGen(models.Model):
    _name = 'membership.individual.id.gen'
    _description = 'Individual ID Sequence Generator'

    membership_id = fields.Char(string='Membership ID', size=15, index=True)
    src = fields.Char(string='Src', size=1)

    _sql_constraints = [
        ('unique_membership_id',
         'unique(membership_id)', 'Membership ID should be unique!')]

    @api.model
    def create(self, values):
        values['src'] = 'C'
        rec = super(IndividualIdGen, self).create(values)
        # create unamhe individual member ID
        rec_id_str = "%s" % rec.id
        member_id = "UNAMHE%s" % rec_id_str.rjust(5, '0')
        rec.membership_id = member_id
        rec.write({'membership_id': member_id})
        return rec


class CorporateIdGen(models.Model):
    _name = 'membership.corporate.id.gen'
    _description = 'Corporate ID Sequence Generator'

    membership_id = fields.Char(string='Membership ID', size=15, index=True)
    src = fields.Char(string='Src', size=1)

    _sql_constraints = [
        ('unique_membership_id',
         'unique(membership_id)', 'Membership ID should be unique!')]

    @api.model
    def create(self, values):
        values['src'] = 'C'
        rec = super(CorporateIdGen, self).create(values)
        # create unamhe corporate member ID
        rec_id_str = "%s" % rec.id
        member_id = "CMP%s" % rec_id_str.rjust(5, '0')
        rec.membership_id = member_id
        rec.write({'membership_id': member_id})
        return rec
