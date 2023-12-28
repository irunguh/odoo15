from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"
    _description = "Account Move Line"

    tax_amount = fields.Float(string="Tax Amount", compute="_compute_tax_amount")

    @api.onchange("quantity", "tax_ids")
    def _compute_tax_amount(self):
        for move_line_id in self:
            tax_only = 0
            for tax_id in move_line_id.tax_ids:
                tax_only += move_line_id.price_unit * (tax_id.amount / 100)
            move_line_id.tax_amount = tax_only * move_line_id.quantity
