from odoo import fields, models, api


class SaleOrderTax(models.Model):
    _name = 'sale.order.tax'

    sale_order = fields.Many2one('sale.order', string='Sale Order')
    name = fields.Char(string='Tax Description', required=True)
    amount = fields.Float(string='Amount')
    account_id = fields.Many2one('account.account', string='Tax Account')
    tax_id = fields.Many2one('account.tax', string="Tax")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    taxes = fields.One2many('sale.order.tax', 'sale_order', string='Taxes', compute='_compute_sale_order_taxes')

    @api.depends('order_line.tax_id')
    def _compute_sale_order_taxes(self):
        for rec in self:
            rec.taxes = [(5, 0, 0)]
            for line in rec.order_line:
                previous_taxes_ids = rec.taxes.mapped('tax_id').ids
                if line.tax_id:
                    price = line.price_unit
                    taxes = line.tax_id.compute_all(
                        price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id)['taxes']
                    val_list = []
                    for tax in taxes:
                        if tax['id'] in previous_taxes_ids:
                            purchase_tax = rec.taxes.filtered(lambda taxes: taxes.tax_id.id == tax['id'])
                            purchase_tax.amount += tax['amount']
                        else:
                            val = {
                                'sale_order': rec.id,
                                'name': tax['name'],
                                'tax_id': tax['id'],
                                'amount': tax['amount'],
                                'account_id': tax['account_id'],
                            }
                            val_list.append(val)
                    rec.taxes.create(val_list)

    # def _compute_total_quantity(self):
    #     for sale_order in self:
    #         sale_order.order_quantity = sum(sale_order.order_line.mapped('product_uom_qty'))
    #         sale_order.deliver_quantity = sum(sale_order.order_line.mapped('qty_delivered'))
    #         sale_order.invoice_quantity = sum(sale_order.order_line.mapped('qty_invoiced'))
