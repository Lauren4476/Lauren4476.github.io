---
title: "Publications"
permalink: /publications/
author_profile: true
---

{% if site.author.ads and site.author.orcid %}
  You can also find my articles in <u><a href="{{ site.author.ads }}">my NASA ADS library</a></u> and on <u><a href="{{ site.author.orcid }}">my ORCID profile</a></u>.
{% elsif site.author.orcid %}
  You can also find my articles on <u><a href="{{ site.author.orcid }}">my ORCID profile</a></u>.
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}