# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ruksana P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from odoo import fields, models


class SaleOrderRequest(models.TransientModel):
    """
    This wizard is used for creating expense records.It allows users to
    specify the service, the employee associated with the record, and the total
    amount for the record.
    """
    _name = 'project.materials.request'
    _description = "Project Materials Issue"

    partner_id = fields.Many2one('res.partner', string="Customer",
                                 help="Customer to Charge")
    date_issued = fields.Datetime(string="Date Order",default=fields.Date.today())

    project_id = fields.Many2one('project.project',string='Project')

    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')

    def action_create_sales_order(self):
        """ Create request """
        orders = [self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'date_order': self.date_issued,
            # 'analytic_account_id': self._context.get('analytic_account_id'),
            'analytic_account_id' : self.analytic_account_id.id
            # 'project_id': self._context.get('default_project_id'),
            # 'total_amount': self.total_amount / len(self.employee_ids),
            # 'product_id': self.product_id.id,
            # 'unit_amount': self.product_id.standard_price
        })]
        ## navigate to sale order
        #print(orders[0].id)
        action = {
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', orders[0].id)],
            'view_mode': 'kanban,form',
            'name': ('Sale Orders'),
            'res_model': 'sale.order',
        }
        return action
