from django.urls import path

from tonictail.cms.views import theme_css

urlpatterns = [
    # ... existing urls ...
    path("theme-vars.css", theme_css, name="theme_css"),
    # ... wagtail urls last ...
]