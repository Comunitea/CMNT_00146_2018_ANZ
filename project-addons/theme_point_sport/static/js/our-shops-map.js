// Add Point Sport shop's Google map
function pointShopsInitMap() {
    // Set var
    var icon1 = '/theme_anzamar/static/img/map/place-marker.png'
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

        // La Coruña
        {lat: 42.553912, lng: -8.992299, title: 'Podium Sport', phone: '981 875 440', address: 'Rua de Lugo, 3, Riveira, La Coruña'},
        // Canarias
        {lat: 28.355137, lng: -16.370066, title: 'Deportes Marques', phone: '922 502 044', address: 'Calle Ernesto Salcedo, 7, Candelaria, Tenerife'},
        // Baleares
        //{lat: 39.5678517, lng: 3.2122086, title: 'De Cinco', phone: '607 93 78 14', address: 'Avd. Baix Des Cos, 10, Manacor, Islas Baleares'},
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
            map.setCenter(marker.getPosition())
            map.setZoom(18);
            window.open(map, marker);
        });
    });
    // Add clusters
    var markerCluster = new MarkerClusterer(map, toclaster, {
        maxZoom: 11,
        styles: [{
            textColor: '#333333',
            textSize: '16',
            height: 53,
            width: 53,
            url: '/theme_anzamar/static/img/map/cluster-marker-1.png'
        }]
    });
}
