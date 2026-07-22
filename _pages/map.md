---
layout: archive
title: "Places I've visted"
permalink: /map/
author_profile: True
output: True
---

<p>Universities, conferences, schools, and institutes I've been to during my academic career.</p>

<div id="academic-map" style="height: 600px; width: 100%;"></div>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.0-beta.2/leaflet.css" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.0-beta.2/leaflet.js"></script>
<link rel="stylesheet" href="{{ '/talkmap/leaflet_dist/MarkerCluster.css' | relative_url }}" />
<link rel="stylesheet" href="{{ '/talkmap/leaflet_dist/MarkerCluster.Default.css' | relative_url }}" />
<script src="{{ '/talkmap/leaflet_dist/leaflet.markercluster-src.js' | relative_url }}"></script>
<script src="{{ '/talkmap/org-locations.js' | relative_url }}"></script>

<script type="text/javascript">
  var tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
  });
  var map = L.map('academic-map', { center: [30, 10], zoom: 2, layers: [tiles] });
  var markers = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 80 });
  for (var i = 0; i < addressPoints.length; i++) {
    var a = addressPoints[i];
    var marker = L.marker(new L.LatLng(a[1], a[2]), { title: a[0] });
    marker.bindPopup(a[0]);
    markers.addLayer(marker);
  }
  map.addLayer(markers);
</script>