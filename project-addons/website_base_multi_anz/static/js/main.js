/* Hide top menu part with scroll */
$(window).on('scroll', function() {
    if ($(window).scrollTop() > 60) {
        $('.wp-contact-navbar').hide();
        if(!$('header').hasClass('homepage-header') || window.screen.width < 769){
            $('.header-fixed-margin').show();
            if(window.screen.width < 769){
                $('#wrap').css({'margin-top': '79px'});
            }else{
                $('#wrap').css({'margin-top': '95px'});
            }
        }
        $('header').addClass('fixed');
    } else {
        $('header').removeClass('fixed');
        if(!$('header').hasClass('homepage-header') || window.screen.width < 769){
            $('#wrap').css({'margin-top': '0px'});
            $('.header-fixed-margin').hide();
        }
        $('.wp-contact-navbar').show();
    }
});

$(document).ready(function(){
    /*
        Open sub-menu with hover action
    */
    $('#top_menu li.dropdown').hover(function(){
        $(this).addClass('open');
        $(this).find('a.dropdown-toggle').attr('aria-expanded', 'true');
    }, function(){
        $(this).find('a.dropdown-toggle').attr('aria-expanded', 'false');
        $(this).removeClass('open');
    });
});

$(document).ready(function(){
    odoo.define('website_base_multi_anz.multi_update_cart', function (require) {
        'use strict';
        var ajax = require('web.ajax');
        var has_order = false
        var core = require('web.core');
        var _t = core._t;

        $('form#multi_update').on('submit', function(e){
            e.preventDefault();

            var product_variants = {}

            $('.one-input input').each(function(){
                var count = parseInt($(this).val())
                if(count > 0) {
                    if(count > 100){count = 100} // Set MAX limit for any size to 100
                    var key = parseInt($(this).attr('id'))
                    product_variants[key] = count
                }
            });
            ajax.jsonRpc('/shop/cart/create_order', 'call', {}).then(function (result) {
                has_order = result;
                if(has_order === true && Object.keys(product_variants).length > 0){
                    ajax.jsonRpc('/shop/cart/multi_update', 'call', {
                        'update_data': JSON.stringify(product_variants),
                        'product_template': parseInt($('input[name="product_template"]').val())
                    }).then(function (data) {
                        data = $.parseJSON(data);
                        if(data['success'] == true){
                            // SUCCESS ACTION
                            if(data['quantity'] > 0){
                                $('.my_cart_quantity').html(data['quantity']);
                            }
                            $('#multi_was_added .modal-body').html(data['message']);
                            $('#multi_was_added').modal('show');
                            $('form#multi_update').trigger('reset');
                        }else {
                            // ERROR MESSAGE
                            $('#multi_error .modal-body').html(data['message']);
                            $('#multi_error').modal('show');
                        }
                    });
                }else{
                    // ERROR MESSAGE
                    var message = _t('Error');

                    if(has_order === true){
                        message = _t('Empty product list. Please, select one.');
                    }else{
                        message = _t('User access error');
                    }

                    $('#multi_error .modal-body').html("<p><strong>"+message+"</strong></p>");
                    $('#multi_error').modal('show');
                }
            });
        });
        // Reload the product page with closing the success window
        $('#multi_was_added').on('hidden.bs.modal', function(){location.reload()});
    });
});
