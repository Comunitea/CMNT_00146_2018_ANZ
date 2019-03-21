// Add national presence Google map
function pointShopsInitMap() {
    // Set var
    var icon1 = '/theme_anzamar/static/img/place-marker.png'
        offset = new google.maps.Size(0, 48)
        map_center = {lat: 40.352, lng: -4.155}
        shop_01 = {lat: 37.0472176, lng: -4.861957}
        shop_02 = {lat: 36.710308, lng: -4.4629974}
        shop_03 = {lat: 36.6945063, lng: -4.4517726}
    // Map create
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 6,
        center: map_center
    });
    // Set markers content
    var info_shop_01 = new google.maps.InfoWindow({content: '<div><h3>Deportes Palacios</h3><p>Teléfono: 952 723 495</p><p>Plaza de España, 1, Campillos, Malaga</p></div>', pixelOffset: offset})
        info_shop_02 = new google.maps.InfoWindow({content: '<div><h3>Factory Point Sport</h3><p>Teléfono: 952 239 000</p><p>Calle Mefistofeles, 13, Málaga</p></div>', pixelOffset: offset})
        info_shop_03 = new google.maps.InfoWindow({content: '<div><h3>Master Sport</h3><p>Teléfono: 952 239 000</p><p>Avd. De Velazquez, 71, Málaga</p></div>', pixelOffset: offset})
    // Add markers
    var marker_shop_01 = new google.maps.Marker({position: shop_01, map: map, icon: icon1, title: 'Deportes Palacios'})
        marker_shop_02 = new google.maps.Marker({position: shop_02, map: map, icon: icon1, title: 'Factory Point Sport'})
        marker_shop_03 = new google.maps.Marker({position: shop_03, map: map, icon: icon1, title: 'Master Sport'})

    // Add marker click action
    marker_shop_01.addListener('click', function() {info_shop_01.open(map, marker_shop_01);});
    marker_shop_02.addListener('click', function() {info_shop_02.open(map, marker_shop_02);});
    marker_shop_03.addListener('click', function() {info_shop_03.open(map, marker_shop_03);});
}
