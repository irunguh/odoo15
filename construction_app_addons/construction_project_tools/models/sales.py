from odoo import models,api,fields,_
from odoo.exceptions import AccessError, UserError, ValidationError
from itertools import groupby
class SalesExtend(models.Model):
    _inherit = 'sale.order'

    #override this function - Remove the element of  changing date_order which allows users create back orders
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            #'date_order': fields.Datetime.now()
        })
        # we write the Journal Entry if its exists - Assumption is that this is a project
        # this allows us to track what we have delivered and its not yet invoiced.
        if self.analytic_account_id:
           # we have an account set so we write the debits side
           amount_to_debit = 0
           for item in self.env['sale.order.line'].search([('order_id','=',self.id)]):
               amount_to_debit = item.product_id.standard_price * item.product_uom_qty
               # we now write the analtyical account
               create_analytical_line = self.env['account.analytic.line'].create({
                'name': item.name,
                'date':self.date_order,
                'account_id': self.analytic_account_id.id,
                'group_id': self.analytic_account_id.group_id.id,
                #'tag_ids': [(6, 0, )],
                'unit_amount': item.product_uom_qty,
                'product_id': item.product_id and item.product_id.id or False,
                'product_uom_id': item.product_uom and item.product_uom.id or False,
                'amount': - amount_to_debit,
                # 'general_account_id': item.product_id.categ_id.property_account_income_categ_id.id,
                'ref': item.name,
                #'move_id': move_line.id,
                'user_id':  self._uid,
                'partner_id': self.partner_id.id,
                'company_id': self.env.user.company_id.id,
                'category': 'other',
                })
               #print("Debug ------- general account id {0} ".format(item.product_id.categ_id.property_account_income_categ_id.id))


           #raise UserError(_("Debug::: We return {0}".format(amount_to_debit)))
        self._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True