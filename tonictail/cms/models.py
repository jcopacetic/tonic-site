"""
File: tonictail/cms/models.py
Description: Wagtail page models and site settings for the Tonictail CMS.
             Includes a GeneralPage with the full Tonic block library available,
             plus specialised page types for home, landing, blog, and docs.
Author: Jonathan Sumner | jonathan@khaoticdigital.com
"""

from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.blocks import RichTextBlock
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.search import index

from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.snippets.models import register_snippet
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase


from .blocks import CONTENT_BLOCKS

from django.db import models

class NavItem(models.Model):
    menu = ParentalKey('NavMenu', related_name='items', on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    page = models.ForeignKey(
        'wagtailcore.Page',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    custom_url = models.CharField(max_length=500, blank=True)
    open_in_new_tab = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def url(self):
        if self.page:
            return self.page.url
        return self.custom_url

@register_snippet
class NavMenu(ClusterableModel):
    name = models.CharField(max_length=100)

    panels = [
        FieldPanel('name'),
        InlinePanel('items', label='Navigation items'),
    ]

    def __str__(self):
        return self.name


# ============================================================
# CUSTOM IMAGE MODEL
# ============================================================

class CustomImage(AbstractImage):
    """
    Extends Wagtail's default image model with an alt_text field.
    Referenced by WAGTAILIMAGES_IMAGE_MODEL = "cms.CustomImage" in settings.
    """
    alt_text = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + ("alt_text",)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage,
        on_delete=models.CASCADE,
        related_name="renditions",
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


# ============================================================
# PAGE MODELS
# ============================================================

class HomePage(Page):
    """
    Site home page. Full block library available.
    Should be created once as the root page.
    """
    body = StreamField(
        CONTENT_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name="Page content",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Home page"

    # Only one home page should ever exist under the root
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = [
        "cms.GeneralPage",
        "cms.LandingPage",
        "cms.BlogIndexPage",
        "cms.DocsIndexPage",
    ]


class GeneralPage(Page):
    """
    All-purpose flexible page. Has access to every block in the Tonic library.
    Use this for: About, Pricing, Contact, FAQ, Team, and any custom marketing pages.
    """
    intro = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional short intro shown in listings and SEO description fallback.",
    )
    body = StreamField(
        CONTENT_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name="Page content",
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels

    class Meta:
        verbose_name = "General page"
        verbose_name_plural = "General pages"

    parent_page_types = [
        "cms.HomePage",
        "cms.GeneralPage",
    ]
    subpage_types = [
        "cms.GeneralPage",
    ]


class LandingPage(Page):
    """
    Conversion-focused landing page.
    Same block library as GeneralPage but no global nav in the template
    (override base.html's site_header block in the landing page template).
    Useful for ad campaigns, lead gen, event signups.
    """
    body = StreamField(
        CONTENT_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name="Page content",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Landing page"
        verbose_name_plural = "Landing pages"

    parent_page_types = [
        "cms.HomePage",
        "cms.GeneralPage",
    ]
    subpage_types = []


# ============================================================
# BLOG
# ============================================================

class BlogIndexPage(Page):
    """
    Blog listing/index page. Child pages are BlogPostPages.
    """
    intro = RichTextField(blank=True, verbose_name="Intro text")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        posts = (
            BlogPostPage.objects
            .child_of(self)
            .live()
            .order_by("-first_published_at")
        )
        # Basic tag filtering
        tag = request.GET.get("tag")
        if tag:
            posts = posts.filter(tags__name=tag)

        context["posts"] = posts
        context["current_tag"] = tag
        return context

    class Meta:
        verbose_name = "Blog index"

    parent_page_types = ["cms.HomePage", "cms.GeneralPage"]
    subpage_types = ["cms.BlogPostPage"]


# Add this class BEFORE BlogPostPage
class BlogPostPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "BlogPostPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )

class BlogPostPage(Page):
    """
    Individual blog post. Body uses the full block library so posts
    can include any Tonic module inline alongside standard rich text.
    """
    tags = ClusterTaggableManager(through=BlogPostPageTag, blank=True)
    intro = models.CharField(
        max_length=500,
        blank=True,
        help_text="Short excerpt shown on listing cards and as SEO description fallback.",
    )
    featured_image = models.ForeignKey(
        CustomImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Featured image",
    )
    author = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_posts",
        verbose_name="Author",
    )
    body = StreamField(
        CONTENT_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name="Post content",
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("intro"),
            FieldPanel("featured_image"),
            FieldPanel("author"),
            FieldPanel("tags"),    
        ], heading="Post metadata"),
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Blog post"
        verbose_name_plural = "Blog posts"

    parent_page_types = ["cms.BlogIndexPage"]
    subpage_types = []


# ============================================================
# DOCS
# ============================================================

class DocsIndexPage(Page):
    """
    Documentation index/hub page.
    """
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["docs"] = (
            DocsPage.objects
            .child_of(self)
            .live()
            .order_by("title")
        )
        return context

    class Meta:
        verbose_name = "Docs index"

    parent_page_types = ["cms.HomePage", "cms.GeneralPage"]
    subpage_types = ["cms.DocsPage", "cms.DocsSectionPage"]


class DocsSectionPage(Page):
    """
    Optional grouping page for a section of docs (e.g. 'Getting Started').
    """
    intro = models.CharField(max_length=300, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["docs"] = (
            DocsPage.objects
            .child_of(self)
            .live()
            .order_by("title")
        )
        return context

    class Meta:
        verbose_name = "Docs section"

    parent_page_types = ["cms.DocsIndexPage"]
    subpage_types = ["cms.DocsPage"]


class DocsPage(Page):
    """
    Individual documentation page. Intentionally uses a limited block set
    to keep docs focused on content rather than full marketing modules.
    """

    DOCS_BLOCKS = [
        ("rich_text", RichTextBlock(
            features=["h2", "h3", "h4", "bold", "italic", "link",
                      "ol", "ul", "blockquote", "image", "code"],
            label="Rich text",
        )),
    ]

    body = StreamField(
        DOCS_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name="Page content",
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Doc page"
        verbose_name_plural = "Doc pages"

    parent_page_types = ["cms.DocsIndexPage", "cms.DocsSectionPage"]
    subpage_types = []


# ============================================================
# SITE SETTINGS
# ============================================================

class FooterNavColumn(models.Model):
    """
    A single nav column in the footer. Each column has a heading and points
    to a NavMenu snippet whose items become the link list.
    """
    settings = ParentalKey(
        'FooterSettings',
        related_name='nav_columns',
        on_delete=models.CASCADE,
    )
    heading = models.CharField(
        max_length=100,
        help_text="Column heading displayed above the links (e.g. 'Product', 'Company').",
    )
    menu = models.ForeignKey(
        NavMenu,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Choose a nav menu whose items will appear as links in this column.",
    )
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel('heading'),
        FieldPanel('menu'),
        FieldPanel('order'),
    ]

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.heading


@register_setting
class FooterSettings(BaseSiteSetting, ClusterableModel):
    """
    Footer layout settings. Controls the nav columns shown to the right of
    the brand column. The logo/tagline/social links come from SiteSettings.
    """
    panels = [
        InlinePanel('nav_columns', label='Footer nav columns', max_num=4),
    ]

    class Meta:
        verbose_name = "Footer settings"

    def __str__(self):
        # Override to avoid the default BaseSiteSetting.__str__ which accesses
        # self.site (a deferred FK), triggering a sync ORM query that raises
        # SynchronousOnlyOperation when evaluated inside an ASGI async context
        # (e.g. by Django Debug Toolbar's TemplatesPanel.generate_stats).
        return "Footer settings"


@register_setting
class SiteSettings(BaseSiteSetting):
    """
    Global site-wide settings editable from Wagtail admin → Settings.
    Used in base.html for header logo, footer text, social links, etc.
    """
    site_name = models.CharField(max_length=100, default="Tonictail")
    site_logo = models.ForeignKey(
        CustomImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Site logo",
    )
    footer_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Footer tagline",
    )
    twitter_url = models.URLField(blank=True, verbose_name="Twitter / X URL")
    github_url = models.URLField(blank=True, verbose_name="GitHub URL")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")

    panels = [
        MultiFieldPanel([
            FieldPanel("site_name"),
            FieldPanel("site_logo"),
        ], heading="Brand"),
        MultiFieldPanel([
            FieldPanel("footer_text"),
        ], heading="Footer"),
        MultiFieldPanel([
            FieldPanel("twitter_url"),
            FieldPanel("github_url"),
            FieldPanel("linkedin_url"),
        ], heading="Social links"),
    ]

    class Meta:
        verbose_name = "Site settings"

    def __str__(self):
        # Safe override — site_name is a plain CharField, no FK lookup needed.
        return self.site_name or "Site settings"


@register_setting
class ThemeSettings(BaseSiteSetting):
    """
    Theme design tokens. Values are rendered into /theme/theme-vars.css
    as CSS custom properties, driving the entire Tonic CSS framework.
    Change a value here → every component updates on next page load.
    """
    # Brand colors
    color_primary    = models.CharField(max_length=20, default="#06B6D4", verbose_name="Primary color")
    color_secondary  = models.CharField(max_length=20, default="#10B981", verbose_name="Secondary color")
    color_accent     = models.CharField(max_length=20, default="#8B5CF6", verbose_name="Accent color")
    color_highlight  = models.CharField(max_length=20, default="#E0F7FA", verbose_name="Highlight color")

    # Text colors
    color_text_heading = models.CharField(max_length=20, default="#0F172A", verbose_name="Heading color")
    color_text_body    = models.CharField(max_length=20, default="#334155", verbose_name="Body text color")
    color_text_muted   = models.CharField(max_length=20, default="#94A3B8", verbose_name="Muted text color")

    # Background colors
    color_bg_light = models.CharField(max_length=20, default="#FFFFFF", verbose_name="Light background")
    color_bg_dark  = models.CharField(max_length=20, default="#0F172A", verbose_name="Dark background")
    color_bg_alt   = models.CharField(max_length=20, default="#F8FAFC", verbose_name="Alternate background")

    # UI colors
    color_border     = models.CharField(max_length=20, default="#E2E8F0", verbose_name="Border color")
    color_link       = models.CharField(max_length=20, default="#06B6D4", verbose_name="Link color")
    color_link_hover = models.CharField(max_length=20, default="#0891B2", verbose_name="Link hover color")
    color_focus      = models.CharField(max_length=20, default="#06B6D4", verbose_name="Focus ring color")

    # Typography
    font_heading = models.CharField(max_length=100, default="Inter", verbose_name="Heading font")
    font_body    = models.CharField(max_length=100, default="Inter", verbose_name="Body font")
    font_display = models.CharField(max_length=100, default="Inter", verbose_name="Display font")
    font_mono    = models.CharField(max_length=100, default="JetBrains Mono", verbose_name="Mono font")

    font_size_display = models.PositiveIntegerField(default=72, verbose_name="Display size (px)")
    font_size_heading = models.PositiveIntegerField(default=48, verbose_name="Heading size (px)")
    font_size_body    = models.PositiveIntegerField(default=16, verbose_name="Body size (px)")
    font_size_small   = models.PositiveIntegerField(default=14, verbose_name="Small size (px)")

    font_weight_heading = models.PositiveIntegerField(default=700, verbose_name="Heading weight")
    font_weight_body    = models.PositiveIntegerField(default=400, verbose_name="Body weight")
    line_height_body    = models.CharField(max_length=10, default="1.6", verbose_name="Body line height")

    # Spacing & layout
    section_padding        = models.PositiveIntegerField(default=80, verbose_name="Section padding desktop (px)")
    section_padding_mobile = models.PositiveIntegerField(default=48, verbose_name="Section padding mobile (px)")
    container_max          = models.PositiveIntegerField(default=1280, verbose_name="Container max width (px)")
    container_gutter       = models.PositiveIntegerField(default=24, verbose_name="Container gutter (px)")
    grid_gutter            = models.PositiveIntegerField(default=24, verbose_name="Grid gutter (px)")
    row_gap                = models.PositiveIntegerField(default=16, verbose_name="Row gap (px)")

    # Borders & radius
    border_radius      = models.PositiveIntegerField(default=6, verbose_name="Default radius (px)")
    border_radius_btn  = models.PositiveIntegerField(default=6, verbose_name="Button radius (px)")
    border_radius_card = models.PositiveIntegerField(default=12, verbose_name="Card radius (px)")
    border_radius_img  = models.PositiveIntegerField(default=8, verbose_name="Image radius (px)")
    border_color       = models.CharField(max_length=20, default="#E2E8F0", verbose_name="Border color")
    border_width       = models.PositiveIntegerField(default=1, verbose_name="Border width (px)")

    # Shadows
    SHADOW_CHOICES = [
        ("none",     "None"),
        ("subtle",   "Subtle"),
        ("medium",   "Medium"),
        ("elevated", "Elevated"),
    ]
    shadow_card   = models.CharField(max_length=20, choices=SHADOW_CHOICES, default="subtle")
    shadow_button = models.CharField(max_length=20, choices=SHADOW_CHOICES, default="none")

    # Buttons — primary
    btn_primary_bg     = models.CharField(max_length=20, default="#06B6D4")
    btn_primary_hover  = models.CharField(max_length=20, default="#0891B2")
    btn_primary_active = models.CharField(max_length=20, default="#0E7490")
    btn_primary_text   = models.CharField(max_length=20, default="#FFFFFF")
    btn_primary_border = models.CharField(max_length=20, default="#06B6D4")

    # Buttons — secondary
    btn_secondary_bg     = models.CharField(max_length=20, default="#10B981")
    btn_secondary_hover  = models.CharField(max_length=20, default="#059669")
    btn_secondary_active = models.CharField(max_length=20, default="#047857")
    btn_secondary_text   = models.CharField(max_length=20, default="#FFFFFF")
    btn_secondary_border = models.CharField(max_length=20, default="#10B981")

    # Buttons — ghost
    btn_ghost_text   = models.CharField(max_length=20, default="#06B6D4")
    btn_ghost_border = models.CharField(max_length=20, default="#06B6D4")

    # Buttons — subtle
    btn_subtle_bg     = models.CharField(max_length=20, default="#F0FDFA")
    btn_subtle_hover  = models.CharField(max_length=20, default="#CCFBF1")
    btn_subtle_active = models.CharField(max_length=20, default="#99F6E4")
    btn_subtle_text   = models.CharField(max_length=20, default="#0F766E")
    btn_subtle_border = models.CharField(max_length=20, default="#99F6E4")

    # Button typography
    BTN_TRANSFORM_CHOICES = [
        ("none",       "None"),
        ("uppercase",  "Uppercase"),
        ("capitalize", "Capitalize"),
    ]
    BTN_WEIGHT_CHOICES = [
        ("400", "Regular"),
        ("500", "Medium"),
        ("600", "Semibold"),
        ("700", "Bold"),
    ]
    btn_text_transform = models.CharField(max_length=20, choices=BTN_TRANSFORM_CHOICES, default="none")
    btn_font_weight    = models.CharField(max_length=10, choices=BTN_WEIGHT_CHOICES, default="600")

    # Forms
    form_input_radius = models.PositiveIntegerField(default=6)
    form_input_border = models.CharField(max_length=20, default="#CBD5E1")

    # Extras
    section_divider_color   = models.CharField(max_length=20, default="#E2E8F0")
    blockquote_border_color = models.CharField(max_length=20, default="#06B6D4")
    BLOCKQUOTE_STYLE = [("normal", "Normal"), ("italic", "Italic")]
    blockquote_font_style = models.CharField(max_length=10, choices=BLOCKQUOTE_STYLE, default="italic")

    panels = [
        MultiFieldPanel([
            FieldPanel("color_primary"),
            FieldPanel("color_secondary"),
            FieldPanel("color_accent"),
            FieldPanel("color_highlight"),
        ], heading="Brand colors"),
        MultiFieldPanel([
            FieldPanel("color_text_heading"),
            FieldPanel("color_text_body"),
            FieldPanel("color_text_muted"),
        ], heading="Text colors"),
        MultiFieldPanel([
            FieldPanel("color_bg_light"),
            FieldPanel("color_bg_dark"),
            FieldPanel("color_bg_alt"),
        ], heading="Backgrounds"),
        MultiFieldPanel([
            FieldPanel("color_border"),
            FieldPanel("color_link"),
            FieldPanel("color_link_hover"),
            FieldPanel("color_focus"),
        ], heading="UI colors"),
        MultiFieldPanel([
            FieldPanel("font_heading"),
            FieldPanel("font_body"),
            FieldPanel("font_display"),
            FieldPanel("font_mono"),
            FieldPanel("font_size_display"),
            FieldPanel("font_size_heading"),
            FieldPanel("font_size_body"),
            FieldPanel("font_size_small"),
            FieldPanel("font_weight_heading"),
            FieldPanel("font_weight_body"),
            FieldPanel("line_height_body"),
        ], heading="Typography"),
        MultiFieldPanel([
            FieldPanel("section_padding"),
            FieldPanel("section_padding_mobile"),
            FieldPanel("container_max"),
            FieldPanel("container_gutter"),
            FieldPanel("grid_gutter"),
            FieldPanel("row_gap"),
        ], heading="Spacing & layout"),
        MultiFieldPanel([
            FieldPanel("border_radius"),
            FieldPanel("border_radius_btn"),
            FieldPanel("border_radius_card"),
            FieldPanel("border_radius_img"),
            FieldPanel("border_color"),
            FieldPanel("border_width"),
            FieldPanel("shadow_card"),
            FieldPanel("shadow_button"),
        ], heading="Borders & shadows"),
        MultiFieldPanel([
            FieldPanel("btn_primary_bg"),
            FieldPanel("btn_primary_hover"),
            FieldPanel("btn_primary_active"),
            FieldPanel("btn_primary_text"),
            FieldPanel("btn_primary_border"),
        ], heading="Primary button"),
        MultiFieldPanel([
            FieldPanel("btn_secondary_bg"),
            FieldPanel("btn_secondary_hover"),
            FieldPanel("btn_secondary_active"),
            FieldPanel("btn_secondary_text"),
            FieldPanel("btn_secondary_border"),
        ], heading="Secondary button"),
        MultiFieldPanel([
            FieldPanel("btn_ghost_text"),
            FieldPanel("btn_ghost_border"),
            FieldPanel("btn_subtle_bg"),
            FieldPanel("btn_subtle_hover"),
            FieldPanel("btn_subtle_active"),
            FieldPanel("btn_subtle_text"),
            FieldPanel("btn_subtle_border"),
        ], heading="Ghost & subtle buttons"),
        MultiFieldPanel([
            FieldPanel("btn_text_transform"),
            FieldPanel("btn_font_weight"),
        ], heading="Button typography"),
        MultiFieldPanel([
            FieldPanel("form_input_radius"),
            FieldPanel("form_input_border"),
        ], heading="Forms"),
        MultiFieldPanel([
            FieldPanel("section_divider_color"),
            FieldPanel("blockquote_border_color"),
            FieldPanel("blockquote_font_style"),
        ], heading="UI extras"),
    ]

    class Meta:
        verbose_name = "Theme settings"

    def __str__(self):
        return "Theme settings"