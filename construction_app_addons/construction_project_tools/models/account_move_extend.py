from odoo import api, fields, models, Command, _

class AccountMoveLineExtend(models.Model):
    _inherit='account.move.line'
    # Override - We want to avoid creation of debits again since we create during sales order confirmation
    def create_analytic_lines(self):
        """ Create analytic items upon validation of an account.move.line having an analytic account or an analytic distribution.
        """
        #print("Debug ********************** create_analytic_lines ")
        lines_to_create_analytic_entries = self.env['account.move.line']
        analytic_line_vals = []
        for obj_line in self:
            for tag in obj_line.analytic_tag_ids.filtered('active_analytic_distribution'):
                for distribution in tag.analytic_distribution_ids:
                    analytic_line_vals.append(obj_line._prepare_analytic_distribution_line(distribution))

            if obj_line.analytic_account_id and obj_line.credit:
                lines_to_create_analytic_entries |= obj_line


        # create analytic entries in batch
        if lines_to_create_analytic_entries:
            analytic_line_vals += lines_to_create_analytic_entries._prepare_analytic_line()

        self.env['account.analytic.line'].create(analytic_line_vals)