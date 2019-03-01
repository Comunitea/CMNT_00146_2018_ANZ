/* Hide top menu part with scroll */
$(window).on('scroll', function() {
    if ($(window).scrollTop() > 135) {
        $('.wp-contact-navbar').hide();
        if(!$('header').hasClass('homepage-header')){$('.header-fixed-margin').show();}
        $('header').addClass('fixed');
    } else {
        $('header').removeClass('fixed');
        if(!$('header').hasClass('homepage-header')){$('.header-fixed-margin').hide();}
        $('.wp-contact-navbar').slideDown(100);
    }
});
