from odoo import models, fields

class Cities(models.Model):
    _name = 'unamhe.cities'
    _description = 'Cities'

    name = fields.Char(required=True)
    district_ids = fields.One2many('unamhe.district', 'city_id', string='Districts')

class District(models.Model):
    _name = 'unamhe.district'
    _description = 'District'

    name = fields.Char(required=True)
    city_id = fields.Many2one('unamhe.cities', required=True)