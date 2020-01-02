// Add Point Sport shop's Google map
function pointShopsInitMap() {
    // Set var
    var icon1 = '/theme_point_sport/static/img/map/place-marker.png'
        offset = new google.maps.Size(0, 46)
        toclaster = []
    // Map create
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 6,
        center: {lat: 40.0, lng: -4.0}
    });
    // List of shops
    var locations = [
        // Malaga
        {lat: 36.7103080, lng: -4.4629974, title: 'Factory Point Sport', phone: '952 239 000', address: 'Calle Mefistofeles, 13, Málaga'},
        {lat: 36.6945063, lng: -4.4517726, title: 'Master Sport', phone: '952 239 000', address: 'Avd. De Velazquez, 71, Málaga'},
        {lat: 36.7159021, lng: -4.4332824, title: 'Feel Point', phone: '952 239 000', address: 'Avd. Aurora, 25, A-403, Malaga'},
        {lat: 36.7017126, lng: -4.4467875, title: 'Josemi Sports', phone: '952 346 240', address: 'Calle Jose Palanca, 18, Local 14, Malaga'},
        {lat: 36.6379372, lng: -4.6897305, title: 'Point Sport', phone: '952 239 000', address: 'Avd. Blas Iinfante, 24, Local 2, Alhaurin el Grande, Malaga'},
        {lat: 36.6025015, lng: -4.5348351, title: 'Deportes Trebol', phone: '952 443 352', address: 'Avd. Blas Iinfante, 24, Local 2, Alhaurin el Grande, Malaga'},
        {lat: 36.5146941, lng: -4.8794816, title: 'Deportes Ojen', phone: '627 760 093', address: 'Calle Serenata, Local D, Marbella, Malaga'},
        {lat: 36.5083911, lng: -4.8870967, title: 'Sport Running', phone: '627 760 093', address: 'Avd. Miguel Cano, 12, Marbella, Malaga'},
        {lat: 36.5126828, lng: -4.8767723, title: 'C&E Sport Multimarcas', phone: '617 032 279', address: 'Calle Vicente Blasco Ibáñez, 5e, Marbella, Málaga'},
        {lat: 36.4851470, lng: -4.9899614, title: 'Zona 3', phone: '658 785 171', address: 'Calle Lagasca, 42, San Pedro de Alcantara, Málaga'},
        {lat: 36.3672440, lng: -5.2256975, title: 'Vendaval Sport', phone: '952 891 246', address: 'Calle Marqués de Larios, 10, San Luis de Sabinillas, Málaga'},
        {lat: 36.8263589, lng: -4.7054858, title: 'T&N Sport', phone: '619 957 020', address: 'Av. Cervantes, 5, Álora, Málaga'},
        {lat: 37.0284400, lng: -4.3336499, title: 'Deportes Trabuco', phone: '951 158 018', address: 'Calle al Andalus, 24, Villanueva del Trabuco, Málaga'},
        // Cadiz
        {lat: 36.8597593, lng: -5.6407066, title: 'Ciclo Sport Valero', phone: '956 731 111', address: 'Calle Boticas, 29, Villamartin, Cadiz'},
        {lat: 36.4622891, lng: -5.7216373, title: 'Deportes Alcala', phone: '956 413 213', address: 'Plaza Alameda de la Cruz, 7, Alcalá de los Gazules, Cádiz'},
        {lat: 36.5216091, lng: -5.8642085, title: 'Deportes Alcala', phone: '956 416 684', address: 'Calle Alta, 8, Paterna de Rivera, Cádiz'},
        {lat: 36.4617827, lng: -5.9297590, title: 'Deportes Alcala', phone: '956 412 064', address: 'Centro Comercial Sidonia, Avd. Del Mar, Local B-5, Medina Sidonia, Cádiz'},
        {lat: 36.3457701, lng: -5.8140990, title: 'Deportes Alcala', phone: '956 424 614', address: 'Calle Barbate, 7, Benalup Casas Viejas, Cádiz'},
        {lat: 36.6073360, lng: -5.8015110, title: 'Deportes Alcala', phone: '956 160 116', address: 'Calle San Francisco, 12, San José del Valle, Cádiz'},
        {lat: 36.1894609, lng: -5.4316349, title: 'Krono Sport', phone: '675 724 092', address: 'C.C. Bahia Plaza, Local 23, Los Barrios, Cádiz'},
        {lat: 36.1879461, lng: -5.4326608, title: 'Black Laces', phone: '675 724 092', address: 'C.C. Bahia Plaza, Local 22, Los Barrios, Cádiz'},
        {lat: 36.2499127, lng: -5.9656116, title: 'Deportes Quintero', phone: '956 447 407', address: 'Avd. San Miguel, 48, Vejer de la Frontera, Cádiz'},
        {lat: 36.1634749, lng: -5.3526079, title: 'Moybas Sport', phone: '956 094 709', address: 'Calle Aurora, 37, La Línea de la Concepción, Cádiz'},
        {lat: 36.1620117, lng: -5.3457297, title: 'Sport One', phone: '697 193 913', address: 'Calle Jardines, 40, La Línea de la Concepción, Cádiz'},
        {lat: 36.2785282, lng: -6.0880861, title: 'Innovasport', phone: '699 871 388', address: 'Calle Venenciadores, 1, Conil de la Frontera, Cádiz'},
        {lat: 36.9349436, lng: -5.2641249, title: 'Deportes Alameda', phone: '956 120 558', address: 'Calle Victoria, 4, Bajo, Olvera, Cádiz'},
        {lat: 36.7808044, lng: -6.3549315, title: 'Deportes Recio', phone: '956 363 998', address: 'Calzado del Ejército, 18, Sanlúcar de Barrameda, Cádiz'},
        {lat: 36.5954453, lng: -6.2454304, title: 'Futbol Solution', phone: '691 665 384', address: 'Calle Rodrigo de Bastidas, 8, El Puerto de Sta María, Cádiz'},
        {lat: 36.7552463, lng: -5.8119909, title: 'Sporty', phone: '685 170 254', address: 'Calle Nicaragua, 44, Arcos de la Frontera, Cádiz'},
        {lat: 36.5314450, lng: -6.3032921, title: 'Deportes Perico', phone: '646 487 692', address: 'Calle Trinidad, 1 , Esq. calle La Rosa, Cádiz, Cádiz'},
        // Huelva
        {lat: 37.2733239, lng: -6.9128560, title: 'Escode', phone: '680 904 087', address: 'Ctra. Sevilla-Huelva, Km 637, Nave Escode, 2ºP, Huelva, Huelva'},
        {lat: 37.8942487, lng: -6.5602963, title: 'Deportes La Bolera', phone: '959 126 484', address: 'Calle Jose Nogales, 4, Aracena, Huelva'},
        {lat: 37.2916500, lng: -6.3789700, title: 'Deportes Sodicap', phone: '955 755 128', address: 'Plaza Principe de Asturias, 3, Hinojos, Huelva'},
        {lat: 37.2130740, lng: -7.4076498, title: 'Black Laces', phone: '629 269 368', address: 'Calle Lusitania, 3, Ayamonte, Huelva'},
        {lat: 37.2131428, lng: -7.4076176, title: 'Atlántica Sport & Lifestyle', phone: '629 269 368', address: 'Calle Lusitania, 8, Ayamonte, Huelva'},
        {lat: 37.2134771, lng: -7.4082258, title: 'Atlántica Sport & Lifestyle', phone: '629 269 368', address: 'Calle Cervantes, 5, Ayamonte, Huelva'},
        {lat: 37.9098854, lng: -6.8206403, title: 'Hobby Sport', phone: '639 126 426', address: 'Calle Talero, 6, Cortegana, Huelva'},
        // Granada
        {lat: 37.1594300, lng: -3.5985918, title: 'Desafío + K deporte', phone: '637 566 125', address: 'Avd. Don Bosco, 36, Granada, Granada'},
        {lat: 37.2018500, lng: -3.6215100, title: 'Deportes La Via', phone: '616 947 968', address: 'Calle San Sebastian de la Gomera, 12, Granada, Granada'},
        {lat: 37.1468700, lng: -3.6133023, title: 'Feel Point', phone: '952 239 000', address: 'Centro Comercial Nevada Shopping, L-19, Granada, Granada'},
        {lat: 37.1462295, lng: -3.6132866, title: 'Skipping', phone: '952 239 000', address: 'Centro Comercial Nevada Shopping, L-114, Granada, Granada'},
        {lat: 36.7333926, lng: -3.7389263, title: 'Deportes Camaleon', phone: '958 827 025', address: 'Calle La Unidad, 2-7 Plaza Nueva, La Herradura, Granada'},
        {lat: 36.7339795, lng: -3.6909281, title: 'Deportes Lindaraja', phone: '958 634 230', address: 'Calle Cuesta de la Iglesia, 5, Almuñecar, Granada'},
        {lat: 36.7336694, lng: -3.6927782, title: 'All Sport', phone: '958 632 100', address: 'Calle Velez, 23, Almuñecar, Granada'},
        {lat: 36.7523726, lng: -3.5154135, title: 'Deportes Podium', phone: '958 823 345', address: 'Calle Juan de Dios Fernandez Molina, 1, Bajo A, Motril, Granada'},
        {lat: 36.9891841, lng: -3.5691085, title: 'Deportes Lider', phone: '958 781 592', address: 'Calle Almecino Bloque, 2, Bajo, Durcal, Granada'},
        {lat: 37.0235524, lng: -3.6242035, title: 'Deportes Delfos', phone: '958 790 046', address: 'Calle Alcarceles, 9, Padul, Granada'},
        {lat: 37.2222911, lng: -3.6917003, title: 'Luisfer Sport', phone: '958 437 015', address: 'Avd. Estacion, 31, Atarfe, Granada'},
        {lat: 37.2516137, lng: -3.7497281, title: 'Deportes Julio', phone: '958 450 283', address: 'Calle Real, 119, Pinos Puente, Granada'},
        {lat: 37.3022585, lng: -3.1328959, title: 'Deportes Ñin', phone: '958 662 623', address: 'Calle Baza, Guadix, Granada'},
        {lat: 37.2016525, lng: -3.7717163, title: 'Aross Sport', phone: '679 171 728', address: 'Calle Iglesia, 36, Chauchina, Granada'},
        // Cordoba
        {lat: 37.8932563, lng: -4.7639205, title: 'Global Sport', phone: '957 261 149', address: 'Calle Sagunto, 21, Cordoba, Cordoba'},
        {lat: 37.8886113, lng: -4.7633310, title: 'Arteaga Sport', phone: '637 007 721', address: 'Calle Poeta Muhammad Iqbal, 6, Cordoba, Cordoba'},
        {lat: 37.6984057, lng: -5.2790336, title: 'Deportes Hollywood', phone: '957 645 021', address: 'Calle Ancha, 47, Palma del Rio, Cordoba'},
        {lat: 38.3787276, lng: -4.8493201, title: 'Deportes Cardador', phone: '957 770 598', address: 'Calle Maestro Don Camilo, 3, Pozoblanco, Cordoba'},
        {lat: 37.9817441, lng: -4.2877720, title: 'Ripa Sport', phone: '957 176 963', address: 'Calle Fuensanta, 24, Villa del Rio, Cordoba'},
        {lat: 37.3900960, lng: -4.7709216, title: 'Sport Grab', phone: '957 601 208', address: 'Plaza del Romeral, 19, Puente Genil, Cordoba'},
        {lat: 37.7035654, lng: -5.1016113, title: 'Deportes Gomez Hidalgo', phone: '957 638 605', address: 'Calle Portales, 35, Fuente Palmera, Cordoba'},
        {lat: 37.6927490, lng: -4.4787838, title: 'Caza Sport', phone: '957 371 090', address: 'Redonda de Vieja Salud, 52-A, Castro del Rio, Cordoba'},
        {lat: 37.8662300, lng: -4.3183297, title: 'Airsport', phone: '957 183 541', address: 'Parque de Andalucia, Cañete de las Torres, Cordoba'},
        // Jaen
        {lat: 37.7769742, lng: -3.7915241, title: 'Deportes Zona 5', phone: '953 291 133', address: 'Avd. De Andalucia, 1, Jaen, Jaen'},
        {lat: 37.7769951, lng: -3.7916670, title: 'Black Laces', phone: '953 291 133', address: 'Avd. De Andalucia, 1, Jaen, Jaen'},
        {lat: 37.7688720, lng: -3.7879330, title: 'Deportes Zona 5', phone: '953 291 133', address: 'Calle Del Rastro, 11, Local 1, Jaen, Jaen'},
        {lat: 37.7688640, lng: -3.7878620, title: 'Black Laces', phone: '953 291 133', address: 'Calle Del Rastro, 11, Local 1, Jaen, Jaen'},
        {lat: 37.7864903, lng: -3.6084512, title: 'Real Sport', phone: '953 352 132', address: 'Calle Maestra 137, Bajo, Mancha Real, Jaen'},
        {lat: 37.7864903, lng: -3.6084512, title: 'Real Sport', phone: '953 352 132', address: 'Calle Maestra 137, Bajo, Mancha Real, Jaen'},
        {lat: 37.8412048, lng: -3.3524112, title: 'Deportes Thor', phone: '953 787 560', address: 'Calle General Fresneda 65, Bajo, Jodar, Jaen'},
        {lat: 37.7026800, lng: -2.9374100, title: 'Deportes Cruz', phone: '625 484 801', address: 'Avd. Fontanar, 15, Pozo Alcon, Jaen'},
        // Almeria
        {lat: 37.6482352, lng: -2.0768536, title: 'Deportes Authentic', phone: '950 614 026', address: 'Paseo de la Libertad, 30, Velez Rubio, Almería'},
        {lat: 37.3561185, lng: -2.2986565, title: 'Deportes Roma', phone: '950 441 685', address: 'Calle Ramon y Cajal, 41, Olula del Rio, Almería'},
        {lat: 36.8379174, lng: -2.4628781, title: 'Black Laces Almería', phone: '605 095 064', address: 'Calle Rueda Lopez, 4, Local derecha, Almería, Almería'},
        {lat: 36.8445745, lng: -2.9477998, title: 'Deportes J.Canton', phone: '950 492 486', address: 'Calle Manuel Salmeron, 82, Berja, Almería'},
        // Sevilla
        {lat: 37.4863931, lng: -5.9424797, title: 'Deportes San Jose', phone: '954 790 773', address: 'Calle Cordoba, 27, San Jose de la Rinconada, Sevilla'},
        {lat: 37.3232155, lng: -5.4180855, title: 'Servi Sport', phone: '955 847 474', address: 'Calle Fuente de Andalucia, 19, Marchena, Sevilla'},
        {lat: 37.6569450, lng: -5.5250429, title: 'Airesport', phone: '627 580 341', address: 'Avenida de la Campana, Lora del Rio, Sevilla'},
        {lat: 37.8748043, lng: -5.6192854, title: 'Airesport', phone: '627 580 341', address: 'Plaza de España, 10, Constantina, Sevilla'},
        {lat: 37.2467173, lng: -6.3065936, title: 'Deportes Sodicap', phone: '955 755 128', address: 'Calle Pilas, 1, Villamanrique de la Condesa, Sevilla'},
        {lat: 37.1624508, lng: -5.9250179, title: 'Doble M Sport', phone: '616 805 907', address: 'Calle Federico Bustillo, 12, Los Palacios y Villafranca, Sevilla'},
        {lat: 36.9177049, lng: -6.0774865, title: 'Zona Sport', phone: '665 188 589', address: 'Calle Arcos, 39, Lebrija, Sevilla'},
        // Badajoz
        {lat: 38.1646258, lng: -6.6545260, title: 'Odisea Sport', phone: '924 701 446', address: 'Urb. El Puerto Parcela, 12, Fregenal de la Sierra, Badajoz'},
        {lat: 38.7221710, lng: -5.5467238, title: 'Tena Sport', phone: '645 874 906', address: 'Calle Tena Artigas, 7, Castuera, Badajoz'},
        {lat: 38.9078836, lng: -6.6163604, title: 'Point Sport Montijo', phone: '685 890 501', address: 'Calle San Juan de Ribera, 4, Montijo, Badajoz'},
        // Caceres
        {lat: 39.8908450, lng: -5.5377150, title: 'Deportes La Cantera', phone: '685 890 501', address: 'Calle Genaro Cajal, 1, Navalmoral De La Mata, Caceres'},
        // Avila
        {lat: 40.6505698, lng: -4.7000080, title: 'Deportes Avila Anzamar 2006', phone: '920 227 060', address: 'Calle Burgohondo, 2, Avila, Avila'},
        // A Coruña
        {lat: 42.5539120, lng: -8.9922990, title: 'Podium Sport', phone: '981 875 440', address: 'Rúa de Lugo, 3, Riveira, A Coruña'},
        {lat: 42.8815755, lng: -8.5272389, title: '442 BOT4S', phone: '881 973 919', address: 'C.C. Area Central, L1 3F, Santiago de Compostela, A Coruña'},
        // Pontevedra
        {lat: 42.4959802, lng: -8.8658897, title: 'Gaelic Sports Shop', phone: '698 177 555', address: 'Rúa Gorgo, 53, Bajo, O Grove, Pontevedra'},
        {lat: 42.4318084, lng: -8.6381835, title: 'Goleada', phone: '606 509 018', address: 'Rúa Fernando Olmedo, 4, Pontevedra, Pontevedra'},
        // Ourense
        {lat: 42.0624822, lng: -7.7263442, title: 'Manila Sportwear', phone: '629 940 484', address: 'Rúa San Roque, 8, Xinzo de Limia, Ourense'},
        // Valencia
        {lat: 39.4494373, lng: -0.3907422, title: 'Izapatillas', phone: '654 394 214', address: 'Avd. Primero de Mayo, 45 Dch, Valencia, Valencia'},
        // Alicante
        {lat: 38.4057118, lng: -0.4371413, title: 'Plusmarka', phone: '965 940 500', address: 'Avd. Rambla Llibertat, 27, Bajo, Sant Joan D´Alacant, Alicante'},
        // Murcia
        {lat: 37.6751725, lng: -1.6981702, title: 'Zona Zero Sport', phone: '660 466 812', address: 'Calle Corredera, 36, Bajo, Lorca, Murcia'},
        {lat: 38.0925826, lng: -1.7956384, title: 'Patricsport', phone: '968 655 246', address: 'Calle Caamano Amaigenda, 3, 1º Bajo, Cehegin, Murcia'},
        {lat: 38.1037840, lng: -1.8614880, title: 'Patricsport', phone: '968 702 815', address: 'Calle Gran Via, 38, Caravaca, Murcia'},
        {lat: 37.4044568, lng: -1.5811032, title: 'Roja Directa Shop', phone: '868 046 426', address: 'Calle Juan Pablo I, 1, Águilas, Murcia'},
        {lat: 37.6119819, lng: -0.9874304, title: 'Jm Lam', phone: '607 761 127', address: 'Calle Alhambra, 4, Cartagena, Murcia'},
        // Asturias
        {lat: 43.2435189, lng: -5.5611653, title: 'Deportes Montés', phone: '985 610 107', address: 'Calle Libertad, 78, Pola De Laviana, Asturias'},
        {lat: 43.2512967, lng: -5.7750005, title: 'Fitness Mieres', phone: '958 461 434', address: 'Calle Palacio Valdes, 2-4, Mieres, Asturias'},
        // Melilla
        {lat: 35.2927132, lng: -2.9405933, title: 'Deportes Rual', phone: '952 681 159', address: 'Calle Chacel, 1, Melilla, Melilla'},
        // Tenerife
        {lat: 28.3611555, lng: -16.3925932, title: 'Deportes Marques', phone: '922 509 169', address: 'Calle Chacajo, 4, Araya Candelaria, Tenerife'},
        {lat: 28.3994745, lng: -16.3572523, title: 'Deportes Marques', phone: '922 509 044', address: 'Calle San Jose, 66, Barranco Hondo Candelaria, Tenerife'},
        {lat: 28.3551370, lng: -16.3700660, title: 'Deportes Marques', phone: '922 502 044', address: 'Calle Ernesto Salcedo, 7, Candelaria, Tenerife'},
        {lat: 28.4414500, lng: -16.3023200, title: 'Deportes Marques', phone: '922 215 419', address: 'Ctra. General del Sur, 21, Chamberi, Tenerife'},
        {lat: 28.3646423, lng: -16.3665489, title: 'Deportes Marques', phone: '922 504 946', address: 'C.C. Puntalarga, Local 05-06, Caletillas, Tenerife'},
        {lat: 28.4248250, lng: -16.3170830, title: 'Deportes Marques', phone: '922 215 419', address: 'Ctra. General del Sur, 61, Chamberi, Tenerife'},
        {lat: 28.4857368, lng: -16.3158262, title: 'Deportes Marques', phone: '922 256 479', address: 'Calle Heraclio Sanchez, 24, La Laguna, Tenerife'},
        {lat: 28.0349956, lng: -16.6372586, title: 'Oleaje Sport', phone: '626 327 554', address: 'Calle Hermanos Alvarez Quintero, 2, San Miguel de Abona/Guarcha, Tenerife'},
        {lat: 28.0071619, lng: -16.6546381, title: 'Deportes Venezuela', phone: '922 785 648', address: 'Calle Venezuela, 9, Las Galletas, Arona, Tenerife'},
        {lat: 28.0071789, lng: -16.6552010, title: 'Deportes Venezuela', phone: '922 785 935', address: 'Calle Venezuela, 14, Las Galletas, Arona, Tenerife'},
        {lat: 28.0070890, lng: -16.6552700, title: 'Deportes Venezuela', phone: '922 731 741', address: 'Calle Venezuela, 19, Las Galletas, Arona, Tenerife'},
        {lat: 28.0295200, lng: -16.5935030, title: 'Deportes Venezuela', phone: '922 170 200', address: 'Avd. General los Abrigos al Medano, 4, Arona, Tenerife'},
        {lat: 28.0697300, lng: -16.6609040, title: 'Sport Project', phone: '620 050 520', address: 'Ctra. General TF66.285 Edif Tarrante, 2, Arona, Tenerife'},
        {lat: 28.4158300, lng: -16.5486810, title: 'Mundisport', phone: '922 381 374', address: 'Calle Cologan, 8, Puerto de la Cruz, Tenerife'},
        {lat: 28.3930645, lng: -16.5200116, title: 'Mundisport', phone: '922 323 583', address: 'Avd. Emilio Luque Moreno, 25, La Orotava, Tenerife'},
        {lat: 28.3938644, lng: -16.5197267, title: 'Sport Marea', phone: '922 335 312', address: 'Calle San Juan Bosco, 2, Local 18, La Orotava, Tenerife'},
        {lat: 28.3198313, lng: -16.4066833, title: 'Deportes Elta', phone: '649 034 845', address: 'Avd. Santa Cruz, 74, Local 1, Güimar, Tenerife'},
        {lat: 28.4697889, lng: -16.2936474, title: 'Jacare Sport', phone: '629 351 595', address: 'Avd. Los Menceyes, 257, La Laguna, Tenerife'},
        // Menorca
        {lat: 39.9336600, lng:  4.13888400, title: 'Esplai Esport', phone: '630 960 850', address: 'Calle Ramal, 6, Alaior, Menorca'},
    ]
    // Add shop's marker and info popup
    var markers = locations.map(function(location){
        // Add marker
        var marker = new google.maps.Marker({
            position: location,
            map: map,
            icon: icon1,
            title: location.title,
        });
        toclaster.push(marker)
        // Add info popup
        var window = new google.maps.InfoWindow({
            content: '<div><h3>'+location.title+'</h3><p>Teléfono: '+location.phone+'</p><p>'+location.address+'</p></div>',
            maxWidth: 250,
            pixelOffset: offset
        });
        // Add marker click action
        return marker.addListener('click', function() {
            // map.setCenter(marker.getPosition())
            // map.setZoom(18);
            window.open(map, marker);
        });
    });
    // Add clusters
    var markerCluster = new MarkerClusterer(map, toclaster, {
        maxZoom: 13,
        styles: [{
            textColor: '#333333',
            textSize: '16',
            height: 53,
            width: 53,
            url: '/theme_point_sport/static/img/map/cluster-marker-1.png'
        }]
    });
}
