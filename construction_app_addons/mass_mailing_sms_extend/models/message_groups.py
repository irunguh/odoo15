from odoo import models,fields,_

class MarketingMessageGroups(models.Model):
    _name = 'marketing.message.groups'

    name = fields.Char(string='Name',required=True)
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
