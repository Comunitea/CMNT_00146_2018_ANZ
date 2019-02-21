// Add national presence Google map
function presenceInitMap() {
    // Set var
    var map_center = {lat: 40.352, lng: -4.155}
        anzamar = {lat: 36.7052, lng: -4.4804}
        comunitea = {lat: 43.0097, lng: -7.5709}
    // Map create
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 6,
        center: map_center
    });
    // Set markers content
    var marker1Content = '<div><h3>Anzamar S.L.</h3><p>Calle Monterrey, 18. Pol. San Luis, 29006, Malaga</p></div>'
        infoWindow1 = new google.maps.InfoWindow({content: marker1Content})
        marker2Content = '<div><h3>Comunitea S.L.</h3><p>Avenida de las Américas, 59, 27004, Lugo</p></div>'
        infoWindow2 = new google.maps.InfoWindow({content: marker2Content})
    // Add markers
    var marker1 = new google.maps.Marker({
            position: anzamar, map: map, label: 'A',
            icon: 'http://localhost:8069/web/image/127945/32x32',
            title: 'Anzamar, S.L.'})
        marker2 = new google.maps.Marker({
            position: comunitea, map: map, label: 'C',
            icon: 'http://localhost:8069/web/image/127945/32x32',
            title: 'Comunitea S.L.'})

    // Add marker click action
    marker1.addListener('click', function() {infoWindow1.open(map, marker1);});
    marker2.addListener('click', function() {infoWindow2.open(map, marker2);});
}
