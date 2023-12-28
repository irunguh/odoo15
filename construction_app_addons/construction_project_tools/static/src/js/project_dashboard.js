odoo.define('ProjectDashboard.ProjectDashboard', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;
    var ActionMenu = AbstractAction.extend({
        template: 'Projectdashboard',
        events: {

        },


        renderElement: function (ev) {
            var self = this;
            $.when(this._super())
                .then(function (ev) {

                  console.log("RenderElement >>>>>>>>>>>") ;

                });
        },
        format_currency: function(currency, amount){

        },
        willStart: function () {
            var self = this;
            self.drpdn_show = false;
            return Promise.all([ajax.loadLibs(this), this._super()]);
        },
    });
    core.action_registry.add('projects_dashboard', ActionMenu);

});