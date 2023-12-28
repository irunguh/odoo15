 console.log("called--------------------------")
odoo.define('bi_sale_loyalty.loyalty', function(require) {
	"use strict";
	var core = require('web.core');
	var Dialog = require('web.Dialog');

	var _t = core._t;
	var QWeb = core.qweb;

	// return Dialog.extend({
	// 	start: function () {
	// 		var self = this;
	// 		console.log("hiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
	// 		return $.when(
	// 			this._super.apply(this, arguments),
	// 		);
	// 	},
	// });

	// $(document).ready(function() {
	// 	// console.log("11111111111111111111111111111")
	// 	$('.loyalty_redeem').on('click', function () {
	// 		// console.log("clickedddddddd")
	// 		$('.loyalty_redeem').attr('disabled',true)
	// 	})
	// });
		
});