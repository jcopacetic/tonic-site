from django.http import HttpResponse
from django.template.loader import render_to_string
from wagtail.models import Site

from .models import ThemeSettings


def theme_css(request):
    site = Site.find_for_request(request)
    theme = ThemeSettings.for_site(site)
    css = render_to_string("cms/theme-vars.css", {"theme": theme}, request=request)
    return HttpResponse(css, content_type="text/css")