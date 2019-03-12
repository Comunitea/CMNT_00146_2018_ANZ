/* Copyright 2018 Tecnativa - David Vidal
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define('pos.custom_anz.models', function (require) {
    'use strict';

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');

    var core = require('web.core');
    var _t = core._t;

    // When we return an order, y product id not exist, load it
    var widgets = require('pos_order_mgmt.widgets');
    var pos = require('point_of_sale.models');
    var WSuper = widgets.OrderListScreenWidget.prototype;
    widgets.OrderListScreenWidget.include({
        order_list_actions: function (event, action) {
            var dataset = event.target.parentNode.dataset;
            var self = this;
            var order_id = dataset.orderId*1
            self._rpc({
                model: 'pos.order.line',
                method: 'search_read',
                args: [[['order_id', '=', order_id]], ['product_id']],
            }).then(function(result) {
                var product_list = []
                for (var i = 0; i < result.length; i++) {
                    var res = result[i];
                    var product_id = res.product_id[0]
                    var product = self.pos.db.get_product_by_id(product_id);
                    if (!product){
                        product_list.push(product_id);
                    }
                }
                self.pos.add_new_products(product_list)
                .done(function () {
                    if (dataset.orderId) {
                        self.load_order(parseInt(dataset.orderId, 10), action);
                    } else {
                        var local_order = '';
                        _.each(self.orders, function (order) {
                            if (order.uid === dataset.uid) {
                                order.return = action === 'return';
                                local_order = self._prepare_order_from_order_data(order);
                            }
                        });
                        if (local_order) {
                            self['action_' + action](local_order);
                        }
                    }
                });
            })
        },
    });

    // Validate button prompts for reason
    screens.PaymentScreenWidget.include({
        validate_order: function(options) {
            var order = this.pos.get_order()
            if (order.return){
                let reason = prompt(_t("Return Reason"), '');
                order.return_reason = reason
            }
            this._super(options);
        },
    });

    // Export new field return reason
    var order_super = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var res = order_super.export_as_JSON.apply(this, arguments);
            if (this.return) {
                res.return_reason = this.return_reason;
            }
            return res;
        },
        to_upper_case: function(){
            // Evito que falle cuando el pedido es recuperado, ya que entonces
            // el campo simplified invoice no existe, y en el name debería
            // estar cargado el pos_reference, que sería el equivalente en
            // backend del pos reference
            var name_ref = this.simplified_invoice || this.name
            var res = name_ref.toLocaleUpperCase()
            return res;
        }
    });

    var rpc = require('web.rpc');
    var PosModelSuper = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        // Avoid load products with no stock
        load_server_data: function(){
            var self = this;
            
            var loaded = PosModelSuper.load_server_data.call(this);
            
            var prod_model = _.find(this.models, function(model){
                return model.model === 'product.product';
            });
            if (prod_model) {
                prod_model.domain.push(['qty_available','>', 0]);
                var loaded_super = prod_model.loaded;
                prod_model.loaded = function(that, products){
                    loaded_super(that, products);
                };
                return loaded;
            }
        },
        // Get non existing products in cache
        get_cached_product_ids: function(){
            var jsons = this.db.get_unpaid_orders();

            var product_list = []
            for (var i = 0; i < jsons.length; i++) {
                var json = jsons[i];
                var lines = json.lines
                for (var j = 0; j < lines.length; j++) {
                    var line = lines[j][2]
                    var product_id = line.product_id
                    var product = this.db.get_product_by_id(json.product_id);
                    if (!product){
                        product_list.push(product_id);
                    }
                }
            }
            return product_list
        },
        // Load non existing products cached in order lines
        after_load_server_data: function(){
            var self = this;
            var cache_product_ids = self.get_cached_product_ids()
            this.add_new_products(cache_product_ids)
            .done(function () {
                PosModelSuper.after_load_server_data.call(self);
            });
        },
        // Load in pos the selected list of product ids
        add_new_products: function(product_ids){
            var self=this;
            if (_.isEmpty(product_ids)){
                return $.Deferred().resolve()
            }
            var domain = [['id', 'in', product_ids]]
            var fields = ['display_name', 'list_price', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id',
                            'barcode', 'default_code', 'to_weight', 'uom_id', 'description_sale', 'description',
                            'product_tmpl_id','tracking']
            return rpc.query({
                model: 'product.product',
                method: 'search_read',
                args: [domain, fields],
            }).then(function (products) {
                var using_company_currency =self.config.currency_id[0] ===self.company.currency_id[0];
                var conversion_rate =self.currency.rate /self.company_currency.rate;
                self.db.add_products(_.map(products, function (product) {
                    if (!using_company_currency) {
                        product.lst_price = round_pr(product.lst_price * conversion_rate,self.currency.rounding);
                    }
                    product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                    return new models.Product({}, product);
                }));
            }).fail(function (error, event) {
                if (parseInt(error.code, 10) === 200) {
                    // Business Logic Error, not a connection problem
                    self.gui.show_popup(
                        'error-traceback', {
                            'title': error.data.message,
                            'body': error.data.debug,
                        }
                    );
                } else {
                    self.gui.show_popup('error', {
                        'title': _t('Connection error'),
                        'body': _t('Can not execute this action because the POS is currently offline'),
                    });
                }
                event.preventDefault();
            });
        }
    });

});
