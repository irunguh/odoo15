from odoo import fields, api, _ ,models

#
class ProjectCustom(models.Model):

    _inherit = 'project.project'


    # compute project sales
    def _project_sales_orders(self):
        #print("Loaded again >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ")
        sales_orders = self.env['sale.order'].search([('analytic_account_id','=',self.analytic_account_id.id),
                                                      ('partner_id','=',self.partner_id.id),('state','=','draft')
                                                      ])
        # ,
        #                                                       ('state','=','sale')
        #print("Goood >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.total_sales_orders = len(sales_orders)
        # pending
        done_sales_orders = self.env['sale.order'].search([('analytic_account_id', '=', self.analytic_account_id.id),
                                                      ('partner_id', '=', self.partner_id.id),('state','in',['sale','done'])
                                                      ])
        self.done_total_sales_orders = len(done_sales_orders)

        # projects payments
        project_payments_data = self.env['account.payment'].search([('analytic_account_id', '=', self.analytic_account_id.id),
                                                      ('partner_id', '=', self.partner_id.id),('state','in',['draft','posted'])
                                                      ])
        amount_total = 0
        for i in project_payments_data:
            amount_total += i.amount

        self.projects_payments = amount_total

        #return
    # add list of consultants
    consultants = fields.One2many('project.consultants', 'project_consultant_id', string='Consultant Lines',
                                     copy=True,auto_join=True)
    # all sub-contractors
    sub_consultants_contractors = fields.One2many('project.subcontractors', 'project_subcontractor_consultant_id', string='Sub-Contractors Consultant Lines',
                                  copy=True, auto_join=True)
    site_manager = fields.Many2one('res.users',string='Site Manager')

    #project contract data
    # actual completion date - marked when project is closed
    actual_project_completion_date = fields.Date(string='Actual Completion Date')
    # expiration date - start date
    duration = fields.Integer(string='Duration(Weeks)')
    # start to now in weeks
    time_elapsed = fields.Integer(string='Time Elapsed(Weeks)')
    # % percentage of time elapsed
    percentage_time_lapsed = fields.Integer(string='Percentage Time lapsed')
    # extension granted in days
    extension_no_of_days = fields.Integer(string='Extension in Number of Days')
    #revised completion date
    revised_completion_date = fields.Date(string='Revised Completion Date')
    # revised duration in weeks
    revised_duration_weeks = fields.Integer(string='Revised Duration(Weeks)')
    ## orders
    total_sales_orders = fields.Integer(string='Pending Total Sales',compute='_project_sales_orders')
    done_total_sales_orders = fields.Integer(string='Done Sales',compute='_project_sales_orders')
    projects_payments = fields.Integer(string='Payments', compute='_project_sales_orders')
    # project stock location for products to move to
    project_site_store = fields.Many2one("stock.location", string="Site Store",required=False,help="Site store where requested materials will be delivered to from site requistions")

    # payments
    def action_projects_payment_view_create(self):
        return {
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'name': _("Projects Analytics / Payments"),
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id), ('state', 'in',
                                                                                   [('draft'),('posted')])],
            'views': [(self.env.ref('account.view_account_payment_tree').id, 'list'),
                      (self.env.ref('account.view_account_payment_form').id, 'form'),
                      (self.env.ref('account.view_account_payment_kanban').id, 'kanban'),
                      ],
            'view_mode': 'tree,form,kanban',
            'context': {'default_analytic_account_id': self.analytic_account_id.id,
                        'default_partner_id': self.partner_id.id}
        }

    def action_generate_sales_order(self):
        """
        Create Expense Button which will go to expense request form where he
        adds the total amount of expense and also pass the value through context
        """
        return {
            'name': 'Create Sale Order Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'project.materials.request',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_analytic_account_id': self.analytic_account_id.id
            }
        }

    # view draft sales orders linked to a project
    def action_view_draft_orders(self):
        return {
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'name': _("Pending Project Orders"),
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id),('state','=','draft')],
            'views': [(self.env.ref('sale.view_order_tree').id, 'list'),
                      (self.env.ref('sale.view_order_form').id, 'form'),
                      (self.env.ref('sale.view_sale_order_kanban').id, 'kanban'),
                      ],
            'view_mode': 'tree,form,kanban',
            'context': {'default_analytic_account_id': self.analytic_account_id.id,'default_partner_id': self.partner_id.id}
        }
    # view done orders
    def action_view_done_orders(self):
        return {
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'name': _("Pending Project Orders"),
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id), ('state', 'in', ['sale','done'])],
            'views': [(self.env.ref('sale.view_order_tree').id, 'list'),
                      (self.env.ref('sale.view_order_form').id, 'form'),
                      (self.env.ref('sale.view_sale_order_kanban').id, 'kanban'),
                      ],
            'view_mode': 'tree,form,kanban',
            'context': {'default_analytic_account_id': self.analytic_account_id.id}
        }