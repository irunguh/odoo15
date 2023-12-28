from odoo import fields, api, _ ,models
from datetime import datetime

class ProjectConsumeMaterials(models.Model):
    _name = 'project.consume.materials'
    _description = 'Materials to Consume'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    order_no = fields.Char(string='Request Number', required=True, copy=False, readonly=True,
                           default=lambda self: _('New'))
    project_id = fields.Many2one('project.project',string="Project")
    date_order = fields.Date(string="Date Consumed",default=datetime.now())
    stock_source = fields.Many2one('stock.location',string="Stock Source")
    stock_destination = fields.Many2one('stock.location', string="Stock Destination")
    requested_by = fields.Many2one("res.users",string="Request By",default = lambda self: self.env.user)
    # set the company
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)

    consume_material_line = fields.One2many('project.consume.materials.line', 'consume_materials_line_items_id', string='Material Lines',
                                    states={'done': [('readonly', True)]}, copy=True,
                                    auto_join=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    # approve
    def action_approve(self):
        # approved_by we get the current logged in user
        self.write({'state':'done'})
        # then we need to create a transfer request for products
        stock_picking_object = self.env["stock.picking"]
        # picking_type_id >>>>>> stock_picking_type (sequence_code = INT , company_id = logged in company)
        search_stock_picking_type = self.env["stock.picking.type"].search([("sequence_code","=","INT"),("company_id","=",self.env.user.company_id.id)])
        #################
        # picking type variables
        picking_vars = {
            "picking_type_id": search_stock_picking_type.id,
            "location_id": self.stock_source.id,
            "location_dest_id": self.stock_destination.id,
            "origin": self.order_no,
            "project_id": self.project_id.id
        }
        ## line items
        picking_lines = []
        for item in self.consume_material_line:
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
                   'project.consume.materials', sequence_date=seq_date) or _('New')
           else:
               vals['order_no'] = self.env['ir.sequence'].next_by_code('project.consume.materials',
                                                                            sequence_date=seq_date) or _('New')

       result = super(ProjectConsumeMaterials, self).create(vals)
       return result

    # product on change update line items
    @api.onchange('project_id')
    def onchange_project_id(self):
           # we want to set the description,unit price from cost_price of product,uom on product selection
           stock_source_id = self.project_id.project_site_store.id
           self.stock_source = stock_source_id
# line items
class ProjectConsumeMaterialsLine(models.Model):
    _name = 'project.consume.materials.line'
    _description = 'Line items for materials to consume request'

    # fields
    consume_materials_line_items_id = fields.Many2one('project.consume.materials', string='Consume materials Request Reference',
                                               required=True, ondelete='cascade', index=True,
                                               copy=False)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Integer(string='Qty', required=True)
    uom = fields.Many2one('uom.uom', string='Unit of Measure')
    ###########
    # product on change update line items
    @api.onchange('product_id')
    def onchange_product_id(self):
        # we want to set the description,unit price from cost_price of product,uom on product selection
        product_uom = self.product_id.uom_id.id
        self.uom = product_uom
