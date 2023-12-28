# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
	"name" : "Sales Loyalty Rewards and Redeem Program in Odoo",
	"version" : "13.0.0.0",
	"category" : "Sales",
	'summary': 'Sale loyalty points customer loyalty points redeem Sales Loyalty and Rewards Program Sales loyalty rewards sales rewards program sale order loyalty history pos loyalty rewards sale loyalty redeem program sale loyalti program  Sale customer loyalty program',
	"description": """
	loyalty point in odoo,
	redeem point in odoo,
	history report in odoo,
	customer point in odoo,
	loyalty configuration in odoo

This module will help you to give loyalty points to customers based on payments for specific amount of period,
Customer can redeem this points via products (Gift products).
This module also allows you to maintain loyalty history,
you can create various types of reports like customer loyalty history report,customer points report.
odoo POS loyalty management customer loyalty programs loyalty points and reward programs pos odoo
odo pos loyalty program pos loyalty and redeem program pos
odoo POS Loyalty and Rewards Program pos loyalty redeem pos loyalty points reward and redeem on pos
odoo pos redeem loyalty pos loyalty rewards pos rewards program pos loyalty redeem on pos
odoo pos loyalty programs pos loyalty cards pos loyalty discount pos
odoo point of sale loyalty program point of sale loyalty and redeem program point of sales
odoo point of sale Loyalty and Rewards Program point of sale loyalty redeem point of sale loyalty points reward and redeem on odoo
odoo point of sale redeem loyalty point of sale loyalty rewards point of sale rewards program
odoo point of sale loyalty redeem point of sales loyalty program point of sales loyalty and redeem program on pos
odoo point of sales Loyalty and Rewards Program point of sales loyalty redeem on point of sales
odoo point of sales loyalty points reward and redeem point of sales redeem loyalty on point of sales
odoo point of sales loyalty rewards point of sales rewards program point of sales loyalty redeem on pos
POS Loyalty and Rewards Redeem odoo apps is used to give POS loyalty redemption points for every purchase to your customers from point of sales screen.
Customer can also redeem this loyalty points for other purchase from the point of sale screen. 
Every single purchase from the point of sale records the Loyalty Rewards based on configuration setup on point of sale backend and those 
pos rewards will be redeemed on POS order from point of sale touch screen order easily. 
Reward redeems visible on applied point of sales order so it will be helpful for see history of the reward point redemption.



odoo Sale loyalty management Sale customer loyalty programs Sale loyalty points and reward programs Sales odoo
odo Sale loyalty program Sale loyalty and redeem program Sale
odoo Sale Loyalty and Rewards Program Sale loyalty redeem Sale loyalty points reward and redeem on Sale
odoo Sale redeem loyalty Sale loyalty rewards Sale rewards program Sale loyalty redeem on Sale
odoo Sale loyalty programs Sale loyalty cards Sale loyalty discount Sale
odoo Sales loyalty program Sales loyalty and redeem program sales
odoo Sales Loyalty and Rewards Program Sales loyalty redeem Sales loyalty points reward and redeem on odoo
odoo Sales redeem loyalty Sales loyalty rewards Sales rewards program Sales
odoo Sales loyalty redeem Sales loyalty program Sales loyalty and redeem program on Sales
odoo sales Loyalty and Rewards Program sales loyalty redeem on sales
odoo sales loyalty points reward and redeem sales redeem loyalty on sales
odoo Sales loyalty rewards sales rewards program sales loyalty redeem on Sales


odoo Sale Order loyalty management Sale Order customer loyalty programs Sale Order loyalty points and reward programs Sale Order odoo
odo Sale Order loyalty program Sale Order loyalty and redeem program Sale Orders redeem loyalty
odoo Sale Order Loyalty and Rewards Program Sale Order loyalty redeem Sale Order loyalty points reward and redeem on Sale Order
odoo Sale Order redeem loyalty Sale Order loyalty rewards Sale Order rewards program Sale Order loyalty redeem on Sale Order
odoo Sale Order loyalty programs Sale Order loyalty cards Sale order loyalty discount Sale Orders loyalti point redeem
odoo Sales Order loyalty program Sales Order loyalty and redeem program sales Orders loyalty program
odoo Sales Order Loyalty and Rewards Program Sales Order loyalty redeem Sales Order loyalty points reward and redeem on odoo
odoo Sales order redeem loyalty Sales order loyalty rewards Sales order rewards program Sales Orders loyalty points
odoo Sales order loyalty redeem Sales order loyalty program Sales order loyalty and redeem program on Sales Orders loyalty rewards
odoo sales order Loyalty and Rewards Program sales loyalty redeem on sales orders loyalty redeem
odoo sales order loyalty points reward and redeem sales order redeem loyalty on sales orders loyalti rewards
odoo Sales order loyalty rewards sales order rewards program sales order loyalty redeem on Sales orders loyalty reward program

odoo SO loyalty management SO customer loyalty programs SO loyalty points and reward programs SO odoo
odo SO loyalty program SO loyalty and redeem program SO
odoo SO Loyalty and Rewards Program SO loyalty redeem SO loyalty points reward and redeem on SO
odoo SO redeem loyalty SO loyalty rewards SO rewards program SO loyalty redeem on SO
odoo SO loyalty programs SO loyalty cards SO loyalty discount SO


Odoo sales Loyalty and Rewards Redeem odoo apps is used to give Sale loyalty redemption points for every purchase to your customers from point of sales screen.
Customer can also redeem this loyalty points for other purchase from the point of sale screen. 
Every single purchase from the point of sale records the Loyalty Rewards based on configuration setup on point of sale backend and those 
Sales rewards will be redeemed on POS order from point of sale touch screen order easily. 
Reward redeems visible on applied point of sales order so it will be helpful for see history of the reward point redemption.
	""",
	"author": "BrowseInfo",
	"website" : "https://www.browseinfo.in",
	"price": 39,
	"currency": 'EUR',
	"depends" : ['base','sale_management','account','stock'],
	"data": [
		'security/security.xml',
		'security/ir.model.access.csv',
		'data/data.xml',
		'views/loyalty_history.xml',
		'wizard/loyalty_point_wiz_view.xml',
		'wizard/history_report_wiz_view.xml',
		'wizard/customer_points_report_wiz_view.xml',
		'views/custom_view.xml',
		'views/partner_view.xml',
		'views/res_config_view.xml',
	],
	'qweb': [
	],
	"auto_install": False,
	"installable": True,
	"live_test_url":'https://youtu.be/iy5h8WjXwto',
	"images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
