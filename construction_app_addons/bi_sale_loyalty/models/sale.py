# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class InheritSaleOrder(models.Model):
	
	_inherit = "sale.order"

	is_redeemed = fields.Boolean('Is Redeemed')
	redeemed_points = fields.Integer("Redeemed points")
