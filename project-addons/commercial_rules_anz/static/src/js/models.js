/* Copyright 2018 Tecnativa - David Vidal
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define('commercial_rules_anz.models', function (require) {
    'use strict';

    var models = require('point_of_sale.models');
    
    var modelsP = models.PosModel.prototype.models;
    // Add no_promo field to product.product
    for (var i = 0; i <= modelsP.length; i++) {
         var item = modelsP[i];
         if (item.model === 'product.product') {
             item.fields.push('product_brand_id')
             break;
        }
    }

    var order_super = models.Order.prototype.evaluate_condition;
    models.Order = models.Order.extend({
        evaluate_condition: function(condition){
            var product_brands = []
            var lines = this.get_orderlines();
            var line;
            for (var i = 0; i < lines.length; i++) {
                line = lines[i]
                if (line.get_product().product_brand_id) {
                    if ( !(line.get_product().product_brand_id[1] in product_brands))
                        product_brands.push(line.get_product().product_brand_id[1])
                }
            }

            // Como no consigo llamar al super pasandole un argumento extra
            // evaluo aquí la condición
            var evaluation = false;
            if (condition.attribute == 'brand')
                evaluation = eval(condition.serialised_pos)
            else
                evaluation = order_super.apply(this, arguments, 'hola');

            return evaluation;
        }
    });
});
