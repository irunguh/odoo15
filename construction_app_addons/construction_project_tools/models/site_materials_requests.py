from odoo import fields, api, _ ,models
from datetime import datetime

class SiteMaterialsRequests(models.Model):

    _name = 'site.materials.request'
    _description = 'Site materials request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    # fields
    name = fields.Char(string='Request Title',required=True)
    order_no = fields.Char(string='Request Number', required=True, copy=False, readonly=True,default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    date_order = fields.Date(string='Date Ordered',required=True,default=datetime.now())
    notes = fields.Text(string='Additional Notes')
    requested_by = fields.Many2one('res.users',string='Requested By',default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users',string='Responsible', help='The person who approved / declined this request ')
    material_line = fields.One2many('site.materials.request.items', 'site_material_request_id', string='Material Lines',
                                    states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                    auto_join=True)
    cash_line = fields.One2many('site.materials.request.itemscashlines', 'site_material_request_id', string='Cash Lines',
                                    states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                    auto_join=True)
    project_id = fields.Many2one('project.project',string='Project',required=True)
    ## used for display amount with currency
    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute='_compute_currency_id')
    # set the company
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    # total costs
    total_cost_materials_line = fields.Monetary(string='Total Materials Cost',
                             compute='_compute_total_materials_lines', readonly=True, store=True)

    # total costs
    total_cost_cash_line = fields.Monetary(string='Total Cash Requested',
                                 compute='_compute_total_cash_lines', readonly=True, store=True)
    ## totals
    total_materials_cash_cost = fields.Monetary(string='Total Cost',compute='_compute_all_totals',
                                                readonly=True, store=True, help='Total Cost for Cash and Materrials Requested in this order')

    # project budget comparisons with the request
    project_budget_amount = fields.Monetary(string='Project Budget',compute='_compute_project_budget')
    # budgetted balance
    budget_available_balance = fields.Monetary(string='Project Budget',compute='_compute_project_budget_balance')

    # get the approved budget totals for the linked project
    @api.depends('total_materials_cash_cost')
    def _compute_project_budget(self):
        # get project actual budget
        budgets = self.env['project.budget.estimation'].search([('project_id','=',self.project_id.id),
                                                                ('state','=','confirmed')])
        # you can have multiple budgets so loop
        amount = 0
        for b in budgets:
            amount += b.total_cost

        self.project_budget_amount = amount

    # calculate the balance after deducting all items requested for this project
    @api.depends('total_materials_cash_cost')
    def _compute_project_budget_balance(self):
        # we take budget and substract total orders for this project in materials request
        total_orders = 0
        search_items = self.search([('project_id','=',self.project_id.id),('state','!=','declined')])
        if search_items:
            for item in search_items:
                total_orders += item.total_materials_cash_cost
        self.budget_available_balance = self.project_budget_amount - total_orders

    # total costs
    @api.depends('total_cost_materials_line', 'total_cost_cash_line')
    def _compute_all_totals(self):
        # cash costs
        cash_cost = 0
        for cash in self.cash_line:
             cash_cost += cash.sub_total
        # materials cost
        material_cost = 0
        for material in self.material_line:
             material_cost += material.sub_total
        #########
        self.total_materials_cash_cost = cash_cost + material_cost

    # compute material_line totals
    @api.depends('material_line')
    def _compute_total_materials_lines(self):
        # materials cost
        material_cost = 0
        for material in self.material_line:
            material_cost += material.sub_total
        self.total_cost_materials_line = material_cost

    # compute cash line totals
    @api.depends('cash_line')
    def _compute_total_cash_lines(self):
        # materials cost
        cash_cost = 0
        for cash_item in self.cash_line:
            cash_cost += cash_item.sub_total
        self.total_cost_cash_line = cash_cost

    # confirm
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    # reset to draft
    def reset_to_draft(self):
        self.write({'state': 'draft'})
    # approve
    def action_approve(self):
        # approved_by we get the current logged in user
        self.write({'state':'approved', 'approved_by': self._uid })
        # then we need to create a transfer request for products
        stock_picking_object = self.env["stock.picking"]
        # picking_type_id >>>>>> stock_picking_type (sequence_code = INT , company_id = logged in company)
        search_stock_picking_type = self.env["stock.picking.type"].search([("sequence_code","=","INT"),("company_id","=",self.env.user.company_id.id)])
        #################
        # stock source and destination
        stock_source = self.env["stock.location"].search([("usage","=","internal"),("company_id","=",self.env.user.company_id.id)],limit=1)
        stock_destination = self.env["stock.location"].search([("id","=",self.project_id.project_site_store.id)])
        # picking type variables
        picking_vars = {
            "picking_type_id": search_stock_picking_type.id,
            "location_id": stock_source.id,
            "location_dest_id": self.project_id.project_site_store.id,
            "origin": self.order_no,
            "project_id": self.project_id.id
        }
        ## line items
        picking_lines = []
        for item in self.material_line:
            picking_lines.append(
                (
                    0,
                    0,
                    {
                        "name": _('New Move:') + self.order_no,
                        "product_id": item.product_id.id,
                        "product_uom_qty": item.quantity,
                        "product_uom":  item.uom.id
                    },
                )
            )
        # update dictionary
        picking_vars.update({"move_ids_without_package": picking_lines})
        # create final object
        stock_request = stock_picking_object.create(picking_vars)
        #search_picking_type = search_picking_type.search([("")])
    # decline
    def action_decline(self):
        self.write({'state': 'declined', 'approved_by': self._uid})
    # total costs
    @api.depends('material_line')
    def _compute_total_cost(self):
       # materials cost
       material_cost = 0
       for material in self.material_line:
           material_cost += material.sub_total
       self.total_cost = material_cost

    # used for picking currency id
    @api.depends('company_id')
    def _compute_currency_id(self):
       main_company = self.env['res.company']._get_main_company()
       for template in self:
           template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    # Create function
    @api.model
    def create(self, vals):
       if vals.get('order_no', _('New')) == _('New'):
           seq_date = None
           if 'date_order' in vals:
               seq_date = fields.Datetime.context_timestamp(self,
                                                            fields.Datetime.to_datetime(vals['date_order']))
           if 'company_id' in vals:
               vals['order_no'] = self.env['ir.sequence'].with_context(
                   force_company=vals['company_id']).next_by_code(
                   'site.materials.request', sequence_date=seq_date) or _('New')
           else:
               vals['order_no'] = self.env['ir.sequence'].next_by_code('site.materials.request',
                                                                            sequence_date=seq_date) or _('New')

       result = super(SiteMaterialsRequests, self).create(vals)
       return result
# line for cash
class SiteMaterialsRequestsCashLines(models.Model):
    _name = 'site.materials.request.itemscashlines'
    _description = 'Line items for cash requested by site manager'


    #fields
    site_material_request_id = fields.Many2one('site.materials.request', string='Site materials Request Reference',
                                               required=True, ondelete='cascade', index=True,
                               copy=False)
    date_required = fields.Date(string='Date', required=True,default=datetime.now())
    title = fields.Char(string='Used for?',
                        help='Indicate use of this cash for approval',required=True)
    quantity = fields.Integer(string='Qty',required=True)
    unit_price = fields.Monetary(string='Unit Price',required=True)
    sub_total = fields.Monetary(compute='_compute_cash_amount',string='Sub Total',readonly=True, store=True)
    ###
    currency_id = fields.Many2one(related='site_material_request_id.currency_id', depends=['site_material_request_id'],
                                  store=True, string='Currency',
                                  readonly=True)

   # compute price total for materials
    @api.depends('quantity', 'unit_price')
    def _compute_cash_amount(self):
        """
        Compute the amounts of the material line.
        """
        for line in self:
            price = line.unit_price * line.quantity
            line.update({
                'sub_total': price
            })

# line items for materials
class SiteMaterialsRequestsLines(models.Model):
    _name = 'site.materials.request.items'
    _description = 'Line items for site materials request'


    #fields
    site_material_request_id = fields.Many2one('site.materials.request', string='Site materials Request Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    date_required = fields.Date(string='Date', required=True,default=datetime.now())
    job_name = fields.Many2one('project.job.type',string='Job Name',required=True)
    description = fields.Char(string='Description')
    product_id = fields.Many2one('product.product',string='Product',required=True)
    quantity = fields.Integer(string='Qty',required=True)
    uom = fields.Many2one('uom.uom',string='Unit of Measure')
    unit_price_estimate = fields.Monetary(string='Unit Price',required=True)
    sub_total = fields.Monetary(compute='_compute_budget_materials_amount',string='Sub Total',readonly=True, store=True)
    ###
    currency_id = fields.Many2one(related='site_material_request_id.currency_id', depends=['site_material_request_id'], store=True, string='Currency',
                                  readonly=True)

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

