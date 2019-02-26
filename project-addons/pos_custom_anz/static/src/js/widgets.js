/* Copyright 2018 Tecnativa - David Vidal
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define('pos_custom_anz.widgets', function (require) {
    'use strict';

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');

    var core = require('web.core');
    var _t = core._t;

    var gui = require('point_of_sale.gui');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var ScreenWidget = screens.ScreenWidget;
    var chrome = require('point_of_sale.chrome');
    var QWeb = core.qweb;


    
    var ProductListScreenWidget = ScreenWidget.extend({
        template: 'ProductListScreenWidget',

        init: function (parent, options) {
            this._super(parent, options);
            this.new_products = [];
        },

        show: function () {
            var self = this;
            var previous_screen = this.pos.get_order().get_screen_data('previous-screen');
            if (previous_screen === 'receipt') {
                this.gui.screen_instances.receipt.click_next();
                this.gui.show_screen('productlist');
            }
            this._super();
            this.renderElement();
            this.old_order = this.pos.get_order();
            this.$('.back').click(function () {
                return self.gui.show_screen(self.gui.startup_screen);
            });
            var search_timeout = null;
            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }
            this.$('.searchbox input').on('keyup', function (event) {
                    if (event.keyCode == 13) {
                    clearTimeout(search_timeout);
                    var query = this.value;
                    search_timeout = setTimeout(function () {
                        self.perform_search(query, event.which === 13);
                    }, 70);
                }
            });
            this.$('.searchbox .search-clear').click(function () {
                self.clear_search();
            });
        },

        add_product: function(event){
            var dataset = event.target.parentNode.dataset;
            var self = this;
            var product_id = dataset.productid
            var product = this.pos.db.get_product_by_id(product_id);
            if (!product){
                this.pos.add_new_products([product_id])
                .done(function(){
                    var selectedOrder = self.pos.get_order();
                    var product = self.pos.db.get_product_by_id(product_id);
                    selectedOrder.add_product(product);
                    self.gui.show_screen(self.gui.startup_screen);
                }); 
    
            }
        },

        render_list: function () {
            var self = this;
            var products = this.new_products;
            var contents = this.$el[0].querySelector('.product-list-contents');

            for (var i = 0, len = Math.min(products.length, 100); i < len; i++){
                var product = products[i];
                var productline_html = QWeb.render('ProductLine', {
                    widget: this,
                    product: product,
                });
                var productline;
                productline = document.createElement('tbody');
                productline.innerHTML = productline_html;
                productline = productline.childNodes[1];

                contents.appendChild(productline);

                this.$('.product-list-add').off('click');
                this.$('.product-list-add').click(function (event) {
                    self.add_product(event, 'return');
                });
            }
        },

        // Search Part
        search_more_products: function (query) {
            var self = this;
            var domain = ['|', '|', ['name', 'ilike', query], ['barcode', 'ilike', query], ['default_code', 'ilike', query]]
            var fields = ['display_name', 'name', 'list_price', 'barcode', 'default_code']
            return this._rpc({
                model: 'product.product',
                method: 'search_read',
                args: [domain, fields],
            }).then(function (products) {
                self.new_products = products;
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
        },

        perform_search: function (query) {
            var self = this;
            this.search_more_products(query)
                .done(function () {
                    self.render_list();
                });
        },

        clear_search: function () {
            var self = this;
            this.search_more_products()
                .done(function () {
                    self.$('.searchbox input')[0].value = '';
                    self.$('.searchbox input').focus();
                    self.render_list();
                });
        },
    });

    // Add screen product-list
    gui.define_screen({
        name: 'productlist',
        widget: ProductListScreenWidget,
    });

    // Productg button widget
    var ListProductsButtonWidget = PosBaseWidget.extend({
        template: 'ListProductsButtonWidget',
        init: function (parent, options) {
            var opts = options || {};
            this._super(parent, opts);
            this.action = opts.action;
            this.label = opts.label;
        },

        button_click: function () {
            this.gui.show_screen('productlist');
        },

        renderElement: function () {
            var self = this;
            this._super();
            this.$el.click(function () {
                self.button_click();
            });
        },
    });

    // Add button widget
    var widgets = chrome.Chrome.prototype.widgets;
    widgets.push({
        'name': 'list_products',
        'widget': ListProductsButtonWidget,
        'prepend': '.pos-rightheader',
        'args': {
            'label': 'All Products',
        },
    });

});
