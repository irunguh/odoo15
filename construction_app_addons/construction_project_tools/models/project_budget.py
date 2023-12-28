from odoo import fields, api, _ ,models
from datetime import date
from collections import namedtuple
from odoo.exceptions import AccessError, UserError, ValidationError
#main module
class ProjectBudgetEstimation(models.Model):

    _name = 'project.budget.estimation'
    _description = 'Project Budget Estimation'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']


    #fields
    name = fields.Char(string='BOQ Title', required=True)
    #sub_title = fields.Text(string="Short Description",required=True)
    budget_number = fields.Char(string='No.#', required=True, copy=False, readonly=True,default=lambda self: _('New'))
    project_id = fields.Many2one('project.project',string='Project',required=True)
    start_date = fields.Date(string='Date', required=True)
    #end_date = fields.Date(string='Project Est  End Date', required=False)
    description = fields.Text(string='Long Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Active'),
        ('done', 'Quotation'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    total_budget_estimate = fields.Float(string='Total Budget Estimate')
    actual_budget_costs = fields.Float(string='Actual Budget Costs')
    # links
    material_line = fields.One2many('projectbudget.estimation.materials', 'budget_id', string='Material Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)
    ##
    labourers_line = fields.One2many('project.budget.labourers', 'budget_id', string='Labourers Lines',
                                    states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                    auto_join=True)

    ##
    overhead_line = fields.One2many('project.overhead.costs', 'budget_id', string='Overhead / Indirect  Costs',
                                     states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                     auto_join=True)
    ## used for display amount with currency
    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute='_compute_currency_id')
    # total for materials budget
    amount_total_materials = fields.Monetary(string='Materials Total Cost',
                                             compute='_compute_materials_amount_total', readonly=True, store=True
                                             )
    # labourers total
    labourers_amount_total = fields.Monetary(string='Labourers Total Cost',
                                             compute='_compute_labourers_amount_total',readonly=True, store=True)
    # Indirect costs
    overhead_amount_total = fields.Monetary(string='Overhead Total Cost',
                                            compute='_compute_overhead_amount_total',readonly=True, store=True)
    # total costs
    total_cost = fields.Monetary(string='Total Cost',
                                            compute='_compute_total_cost',readonly=True, store=True)

    # set the company
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    ## Actions
    # Confirm budget
    def action_confirm(self):
        # before we confirm we check for overlap
        # we need to prevent users from generating budgets that overlap or confirmed for a project at same times
        #self.check_project_budget_overlap(self.project_id.id, self.start_date, self.end_date)
        # we confirm this
        self.write({'state': 'confirmed'})
    # cancel a budget
    def action_cancel(self):
        self.write({'state': 'cancel'})
    # reset to draft
    def reset_to_draft(self):
        self.write({'state': 'draft'})
    # mark a budget as done
    def action_quotation(self):


        if not self.project_id.partner_id.id:
            raise UserError(_('Please select a customer for this project..'))
        sales_order = self.env['sale.order'].create({
            'partner_id': self.project_id.partner_id.id,
            'state': 'draft',
            'pricelist_id': self.project_id.partner_id.property_product_pricelist.id,
            'validity_date': self.start_date
        })
        # get product to use for creating this sales order line item for transportation
        #products_list = self.env['product.template'].search([('is_transportation_service','=',True)],limit=1)
        ## line items
        for item in self.material_line:
            sales_order_lines = self.env['sale.order.line'].create({'order_id': sales_order.id,
                                                                'product_id': item.product_id.id,
                                                                'name': item.product_id.name,
                                                                'product_uom_qty': item.quantity,
                                                                'product_uom': item.product_id.uom_id.id,
                                                                'price_unit': item.product_id.list_price
                                                                })


        self.write({'state': 'done'})

    # total costs
    @api.depends('overhead_line','material_line','labourers_line')
    def _compute_total_cost(self):
       # overhead costs
       overhead_cost = 0
       for overhead in self.overhead_line:
            overhead_cost += overhead.sub_total
       # materials cost
       material_cost = 0
       for material in self.material_line:
           material_cost += material.sub_total
       # labourers
       labourers_cost = 0
       for labour in self.labourers_line:
           labourers_cost += labour.unit_cost
       #########
       self.total_cost = overhead_cost + material_cost + labourers_cost
       #print('Total Cost Affected!')


    # overhead costs
    @api.depends('overhead_line')
    def _compute_overhead_amount_total(self):
        """
        Compute the amounts of the materials line.
        """
        total_cost = 0
        for cost in self.overhead_line:
            total_cost += cost.sub_total
        ## set the total cost
        self.overhead_amount_total = total_cost
        # return total
        #return self.overhead_amount_total


    # materials costs
    @api.depends('material_line')
    def _compute_materials_amount_total(self):
        """
        Compute the amounts of the materials line.
        """
        total_cost = 0
        for cost in self.material_line:
            total_cost += cost.sub_total
        ## set the total cost
        self.amount_total_materials = total_cost
        # return total
        #return self.amount_total_materials


    # labourers costs
    @api.depends('labourers_line')
    def _compute_labourers_amount_total(self):
        """
        Compute the amounts of the labourers line.
        """
        total_cost = 0
        for cost in self.labourers_line:
            total_cost += cost.unit_cost
        ## set the total cost
        self.labourers_amount_total = total_cost
        # return total
        #return self.labourers_amount_total

    #used for picking currency id
    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id
    # function to check if a budget overlaps for a project
    def check_project_budget_overlap(self,project_id,proposed_start_time,proposed_endtime):
        # we search for current projects budgets and times
        budgets = self.env['project.budget.estimation'].search([('project_id','=',project_id),
                                                                ('state','!=','cancel'),('state','=','confirmed')])
        # we perform validation if we have a similar project
        if budgets:
            # budget active with a similar project
            active_budget_similar_project = budgets[0].id
            print('******')
            print(active_budget_similar_project)
            """check overlapping of two dates with another 2 dates on the same project
             this function is supposed to prevent users from confirming a budget for a project that lies between another
             current project budget confirmed dates """
            current_project_budget_start_date = str(budgets[0].start_date)
            current_project_budget_end_date = str(budgets[0].end_date)
            # now check the overlap
            Range = namedtuple('Range', ['start', 'end'])
            # splitting dates
            # current dates
            current_date_start = current_project_budget_start_date.split('-')
            current_date_end = current_project_budget_end_date.split('-')
            # new dates
            new_start_date = str(proposed_start_time).split('-')
            new_end_date = str(proposed_endtime).split('-')
            ###
            r1 = Range(start=date(int(current_date_start[0]), int(current_date_start[1]), int(current_date_start[2])), end=date(int(current_date_end[0]), int(current_date_end[1]), int(current_date_end[2])))
            r2 = Range(start=date(int(new_start_date[0]), int(new_start_date[1]), int(new_start_date[2])), end=date(int(new_end_date[0]), int(new_end_date[1]), int(new_end_date[2])))
            latest_start = max(r1.start, r2.start)
            earliest_end = min(r1.end, r2.end)
            overlap = (earliest_end - latest_start).days + 1
            overlapping_dates = []  # default
            if overlap > 0:
                overlapping_dates = range(latest_start.toordinal(), earliest_end.toordinal() + 1)  # as numbers
                overlapping_dates = [date.fromordinal(x) for x in overlapping_dates]  # back to datetime.date objects
                raise ValidationError(_('Warning! Please note you cannot confirm budgets for the same project that overlap! Please change the dates or the project to confirm this budget'))



    # Create function
    @api.model
    def create(self, vals):
        if vals.get('budget_number', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['start_date']))
            if 'company_id' in vals:
                vals['budget_number'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'project.budget.estimation', sequence_date=seq_date) or _('New')
            else:
                vals['budget_number'] = self.env['ir.sequence'].next_by_code('project.budget.estimation', sequence_date=seq_date) or _('New')

        result = super(ProjectBudgetEstimation, self).create(vals)
        return result

#overhead costs
class ProjectOverheadCosts(models.Model):
    _name = 'project.overhead.costs'
    _description = 'Project Overhead Costs'


    # fields

    budget_id = fields.Many2one('project.budget.estimation', string='Budget Reference', required=True, ondelete='cascade',
                                    index=True,
                                    copy=False)
    is_overhead = fields.Boolean(string='Is Project Overhead Cost',default=True)
    date_required = fields.Date(string='Date', required=True)
    description = fields.Char(string='Description')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Integer(string='Qty', required=True)
    uom = fields.Many2one('uom.uom', string='Unit of Measure')
    unit_price_estimate = fields.Monetary(string='Unit Price',required=True)
    sub_total = fields.Monetary(compute='_compute_budget_overhead_amount', string='Sub Total', readonly=True, store=True)
    ###
    currency_id = fields.Many2one(related='budget_id.currency_id', depends=['budget_id'], store=True, string='Currency',
                                      readonly=True)

    # compute price total for labourers
    @api.depends('quantity', 'unit_price_estimate')
    def _compute_budget_overhead_amount(self):
        """
        Compute the amounts of the labourers line.
        """
        for line in self:
            price = line.unit_price_estimate * line.quantity
            line.update({
                'sub_total': price
            })

    # set value for sub total
    @api.onchange('quantity','unit_price_estimate')
    def onchange_quantity(self):
        # sub total
        self.sub_total = self.quantity * self.unit_price_estimate

    # product on change update line items
    @api.onchange('product_id')
    def onchange_product_id(self):
        # we want to set the description,unit price from cost_price of product,uom on product selection
        product_uom = self.product_id.uom_id.id
        # standard price
        product_cost_price = self.product_id.standard_price
        ## set these options
        self.description = self.product_id.name
        self.unit_cost = product_cost_price
        self.uom = product_uom

# line items for labourers
class ProjectBudgetLabourers(models.Model):
    _name = 'project.budget.labourers'
    _description = 'Project Budget Labourers'

    #fields
    budget_id = fields.Many2one('project.budget.estimation', string='Budget Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    date_required = fields.Date(string='Date', required=True)
    job_name = fields.Many2one('project.job.type',string='Job Name',required=True)
    description = fields.Char(string='Description')
    #no_of_labourers = fields.Integer(string='Labourers',help='No of Labourers')
    employee = fields.Many2one('hr.employee',string='Employee',required=True)
    unit_cost = fields.Integer(string='Unit Cost',required=True)
    currency_id = fields.Many2one(related='budget_id.currency_id', depends=['budget_id'], store=True, string='Currency',
                                  readonly=True)
    sub_total = fields.Monetary(compute='_compute_labourers_subtotal_amount',string='Sub Total',readonly=True, store=True)

    # compute price total for labourers
    @api.depends('unit_cost')
    def _compute_labourers_subtotal_amount(self):
        """
        Compute the amounts of the labourers line.
        """
        for line in self:
            # price = line.no_of_labourers * line.unit_cost
            line.update({
                'sub_total': line.unit_cost
            })

    # set value for sub total
    @api.onchange('unit_cost')
    def onchange_unit_cost(self):
        # sub total
        self.sub_total = self.unit_cost
    # product on change update line items
    @api.onchange('product_id')
    def onchange_product_id(self):
        # we want to set the description,unit price from cost_price of product,uom on product selection
        product_uom = self.product_id.uom_id.id
        # standard price
        product_cost_price = self.product_id.standard_price
        ## set these options
        self.description = self.product_id.name
        self.unit_cost = product_cost_price
        self.uom = product_uom

#line items for materials
class ProjectBudgetEstimationMaterials(models.Model):
    _name = 'projectbudget.estimation.materials'
    _description = 'Project Budget Estimation Materials'


    #fields
    budget_id = fields.Many2one('project.budget.estimation', string='Budget Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    date_required = fields.Date(string='Date', required=True)
    job_name = fields.Many2one('project.job.type',string='Job Name',required=True)
    description = fields.Char(string='Description')
    product_id = fields.Many2one('product.product',string='Product',required=True)
    quantity = fields.Integer(string='Qty',required=True)
    uom = fields.Many2one('uom.uom',string='Unit of Measure')
    unit_price_estimate = fields.Monetary(string='Unit Price',required=True)
    sub_total = fields.Monetary(compute='_compute_budget_materials_amount',string='Sub Total',readonly=True, store=True)
    ###
    currency_id = fields.Many2one(related='budget_id.currency_id', depends=['budget_id'], store=True, string='Currency',
                                  readonly=True)

    # we calculate totals for these materials
    #@api.depends('sub_total')
    #def _compute_s

    # compute price total for materials
    @api.depends('quantity', 'unit_price_estimate')
    def _compute_budget_materials_amount(self):
        """
        Compute the amounts of the material line.
        """
        for line in self:
            price = line.unit_price_estimate * line.quantity
            line.update({
                'sub_total': price
            })
    # product on change update line items
    @api.onchange('product_id')
    def onchange_product_id(self):
        # we want to set the description,unit price from cost_price of product,uom on product selection
        product_uom = self.product_id.uom_id.id
        # standard price
        product_cost_price = self.product_id.standard_price
        ## set these options
        self.description = self.product_id.name
        self.unit_price_estimate = product_cost_price
        self.uom = product_uom
    # change quantity update sub total
    @api.onchange('quantity')
    def onchange_quantity(self):
        # sub total
        self.sub_total = self.unit_price_estimate * self.quantity


class ProjectTaskType(models.Model):
    _name = 'project.job.type'

    _description = 'Project Task Type'

    name = fields.Char(string='Task Type')