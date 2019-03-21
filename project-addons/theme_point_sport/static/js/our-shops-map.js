// Add Point Sport shop's Google map
function pointShopsInitMap() {
    // Set var
    var icon1 = '/theme_anzamar/static/img/map/place-marker.png'
        offset = new google.maps.Size(0, 46)
        toclaster = []
    // Map create
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 5,
        center: {lat: 38.0, lng: -4.0}
    });
    // List of shops
    var locations = [
        // España peninsular
        {lat: 37.0472176, lng: -4.861957, title: 'Deportes Palacios', phone: '952 723 495', address: 'Plaza de España, 1, Campillos, Malaga'},
        {lat: 36.710308, lng: -4.4629974, title: 'Factory Point Sport', phone: '952 239 000', address: 'Calle Mefistofeles, 13, Málaga'},
        {lat: 36.6945063, lng: -4.4517726, title: 'Master Sport', phone: '952 239 000', address: 'Avd. De Velazquez, 71, Málaga'},
        {lat: 42.5541576, lng: -8.9922087, title: 'Podium Sport', phone: '981 875 440', address: 'Rua de Lugo, 3, Riveira, La Coruña'},
        // Canarias
        {lat: 28.3550807, lng: -16.3703869, title: 'Deportes Marques', phone: '922 502 044', address: 'Calle Ernesto Salcedo, 7, Candelaria, Tenerife'},
        // Baleares
        {lat: 39.5678517, lng: 3.2122086, title: 'De Cinco', phone: '607 93 78 14', address: 'Avd. Baix Des Cos, 10, Manacor, Islas Baleares'},
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
        return marker.addListener('click', function() {window.open(map, marker);});
    });
    // Add clusters
    var markerCluster = new MarkerClusterer(map, toclaster, {
        maxZoom: 9,
        styles: [{
            textColor: '#333333',
            textSize: '16',
            height: 53,
            width: 53,
            url: '/theme_anzamar/static/img/map/cluster-marker-1.png'
        }]
    });
}
