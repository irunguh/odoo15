from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"
    _description = "Account Move"

    print_tax_amount_in_invoice = fields.Boolean(string="Print Tax Amount")