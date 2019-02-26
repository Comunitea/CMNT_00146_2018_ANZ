/* Hide top menu with scroll */
$(window).on('scroll', function() {
    if ($(window).scrollTop() > 200) {
        $('header').addClass('fixed');
        $('.wp-contact-navbar').slideUp();
    } else {
        $('header').removeClass('fixed');
        $('.wp-contact-navbar').slideDown();
    }
});
