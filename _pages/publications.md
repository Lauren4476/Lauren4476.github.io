---
title: "Publications"
permalink: /publications/
author_profile: true
redirect_from: # old individual paper pages
  - /publication/2026-04-01-PRODIGE-Envelope-to-Disk-with-NOEMA-VII-Complex-Organic-Molecules-in-the-NGC1333-IRAS-4B1-Outflow-A-New-Laboratory-for-Shock-Chemistry
---

{% if site.author.ads and site.author.orcid %}
  You can also find my articles in <a href="{{ site.author.ads }}">my NASA ADS library</a> and on <a href="{{ site.author.orcid }}">my ORCID profile</a>.
{% elsif site.author.orcid %}
  You can also find my articles on <a href="{{ site.author.orcid }}">my ORCID profile</a>.
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}