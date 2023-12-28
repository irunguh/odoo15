from odoo import fields, api, _ ,models



class StockPickingExtend(models.Model):

    _inherit = "stock.picking"

    project_id = fields.Many2one("project.project",string="Project")
    truck_number = fields.Char(string='Truck No')
    truck_driver = fields.Char(string='Truck Driver')
    delivery_date = fields.Datetime(string='Delivery Date', default=fields.Datetime.now)