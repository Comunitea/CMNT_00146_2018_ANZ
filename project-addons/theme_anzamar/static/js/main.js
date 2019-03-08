/* Hide top menu part with scroll */
$(window).on('scroll', function() {
    if ($(window).scrollTop() > 145) {
        $('.wp-contact-navbar').hide();
        if(!$('header').hasClass('homepage-header')){
            $('.header-fixed-margin').show();
            $('#wrap').css({'margin-top': '130px'});
        }
        $('header').addClass('fixed');
    } else {
        $('header').removeClass('fixed');
        if(!$('header').hasClass('homepage-header')){
            $('#wrap').css({'margin-top': '0px'});
            $('.header-fixed-margin').hide();
        }
        $('.wp-contact-navbar').show();
    }
});
