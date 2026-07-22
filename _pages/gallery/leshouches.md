---
layout: archive
title: "École de Physique des Houches"
permalink: /gallery/leshouches/
output: True
---

<div class="gallery">
{% for file in site.static_files %}
  {% if file.path contains "images/gallery/leshouches/" %}
    <img src="{{ file.path }}" alt="{{ file.basename }}">
  {% endif %}
{% endfor %}
</div>
