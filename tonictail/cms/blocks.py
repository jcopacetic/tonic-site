"""
File: tonictail/cms/blocks.py
Description: Wagtail StreamField blocks ported from the Tonic HubSpot theme.
             Each HubSpot module maps to a StructBlock with equivalent fields.
             Style/color fields from HubSpot are intentionally omitted — those
             are handled globally by ThemeSettings → theme-vars.css.
             Only content fields are included here.
Author: Jonathan Sumner | jonathan@khaoticdigital.com
Theme: Tonic — Khaotic Digital, LLC
"""

from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    DecimalBlock,
    IntegerBlock,
    ListBlock,
    RawHTMLBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock


# ============================================================
# SHARED / REUSABLE BLOCKS
# ============================================================

class ButtonBlock(StructBlock):
    """Reusable CTA button used across multiple modules."""
    label = CharBlock(max_length=100, required=False, label="Button label")
    url = URLBlock(required=False, label="URL")
    style = ChoiceBlock(choices=[
        ("primary",   "Primary"),
        ("secondary", "Secondary"),
        ("ghost",     "Ghost"),
        ("subtle",    "Subtle"),
        ("link",      "Link"),
    ], default="primary", required=False)
    size = ChoiceBlock(choices=[
        ("sm", "Small"),
        ("md", "Medium"),
        ("lg", "Large"),
    ], default="md", required=False)
    open_in_new_tab = BooleanBlock(default=False, required=False)

    class Meta:
        icon = "link"
        label = "Button"


class SectionHeaderBlock(StructBlock):
    """Shared section header used inside larger blocks."""
    eyebrow = CharBlock(max_length=100, required=False, label="Eyebrow label")
    heading = CharBlock(max_length=200, required=False, label="Heading")
    subheading = RichTextBlock(
        features=["bold", "italic", "link"],
        required=False,
        label="Subheading"
    )
    text_alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
        ("right",  "Right"),
    ], default="left", required=False)

    class Meta:
        icon = "title"
        label = "Section header"


class BackgroundBlock(StructBlock):
    """Shared section background — used inside module blocks."""
    background_type = ChoiceBlock(choices=[
        ("light",       "Light"),
        ("dark",        "Dark"),
        ("alt",         "Alternate"),
        ("primary",     "Brand primary"),
        ("transparent", "Transparent"),
    ], default="light", required=False, label="Background")

    class Meta:
        icon = "image"
        label = "Background"


# ============================================================
# BLOG BLOCKS
# ============================================================

class BlogAuthorBoxBlock(StructBlock):
    """
    Tonic: tonic-blog-author-box
    Displays the post author's bio card below a blog post.
    Wagtail note: author data comes from BlogPostPage.author FK.
    Use this block to configure display options only.
    """
    about_label = CharBlock(
        max_length=100,
        default="About the Author",
        required=False,
        label="Section label"
    )
    show_social = BooleanBlock(default=True, required=False, label="Show social links")
    show_about_label = BooleanBlock(default=True, required=False, label="Show label")
    avatar_size = ChoiceBlock(choices=[
        ("sm", "Small (56px)"),
        ("md", "Medium (72px)"),
        ("lg", "Large (96px)"),
    ], default="md", required=False)

    class Meta:
        icon = "user"
        label = "Author box"
        template = "cms/blocks/blog_author_box_block.html"


class BlogFilterBlock(StructBlock):
    """
    Tonic: tonic-blog-filter
    Tag/category filter bar for blog listing pages.
    Wagtail note: tag list is generated from published posts dynamically in the view.
    """
    all_label = CharBlock(max_length=60, default="All", required=False, label="'All posts' label")
    filter_style = ChoiceBlock(choices=[
        ("pill",      "Pills"),
        ("outline",   "Outline"),
        ("underline", "Underline"),
    ], default="pill", required=False)
    alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
    ], default="left", required=False)

    class Meta:
        icon = "tag"
        label = "Blog filter bar"
        template = "cms/blocks/blog_filter_block.html"


class BlogListingBlock(StructBlock):
    """
    Tonic: tonic-blog-listing
    Grid of blog post cards. Wagtail renders posts dynamically via view context.
    """
    recent_posts_title = CharBlock(max_length=120, default="Latest Articles", required=False)
    read_more_label = CharBlock(max_length=60, default="Read more", required=False)
    card_layout = ChoiceBlock(choices=[
        ("grid",    "Grid"),
        ("list",    "List"),
        ("masonry", "Masonry"),
    ], default="grid", required=False)
    featured_first = BooleanBlock(default=True, required=False, label="Feature first post")
    show_featured_image = BooleanBlock(default=True, required=False)
    show_author = BooleanBlock(default=True, required=False)
    show_date = BooleanBlock(default=True, required=False)
    show_tags = BooleanBlock(default=True, required=False)
    show_excerpt = BooleanBlock(default=True, required=False)

    class Meta:
        icon = "list-ul"
        label = "Blog listing"
        template = "cms/blocks/blog_listing_block.html"


class BlogPaginationBlock(StructBlock):
    """
    Tonic: tonic-blog-pagination
    Previous/next pagination for blog listing.
    Wagtail note: page object provided by view.
    """
    prev_label = CharBlock(max_length=60, default="Previous", required=False)
    next_label = CharBlock(max_length=60, default="Next", required=False)
    pagination_style = ChoiceBlock(choices=[
        ("numbered", "Numbered"),
        ("prev_next", "Prev / Next only"),
    ], default="numbered", required=False)
    alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
        ("right",  "Right"),
    ], default="center", required=False)

    class Meta:
        icon = "arrow-right"
        label = "Blog pagination"
        template = "cms/blocks/blog_pagination_block.html"


class BlogTOCBlock(StructBlock):
    """
    Tonic: tonic-blog-toc
    Table of contents generated from post headings via JS.
    """
    toc_title = CharBlock(max_length=100, default="In this article", required=False)
    mobile_toggle_label = CharBlock(max_length=60, default="Show contents", required=False)
    toc_position = ChoiceBlock(choices=[
        ("inline",  "Inline (top of post)"),
        ("sidebar", "Sidebar (sticky)"),
    ], default="inline", required=False)
    min_headings = IntegerBlock(default=3, min_value=1, max_value=10, required=False,
                                help_text="Minimum headings before TOC shows")

    class Meta:
        icon = "list-ol"
        label = "Table of contents"
        template = "cms/blocks/blog_toc_block.html"


class BlogRelatedPostsBlock(StructBlock):
    """
    Tonic: tonic-blog-related-posts
    Related posts section at the bottom of a blog post.
    """
    section_title = CharBlock(max_length=120, default="Related Articles", required=False)
    read_more_label = CharBlock(max_length=60, default="Read more", required=False)
    post_count = IntegerBlock(default=3, min_value=1, max_value=6, required=False)
    columns_desktop = ChoiceBlock(choices=[
        ("2", "2 columns"),
        ("3", "3 columns"),
    ], default="3", required=False)
    show_featured_image = BooleanBlock(default=True, required=False)
    show_author = BooleanBlock(default=True, required=False)
    show_date = BooleanBlock(default=True, required=False)
    show_excerpt = BooleanBlock(default=True, required=False)

    class Meta:
        icon = "repeat"
        label = "Related posts"
        template = "cms/blocks/blog_related_posts_block.html"


class BlogPostHeaderBlock(StructBlock):
    """
    Tonic: tonic-blog-post-header
    Hero header for a blog post page.
    Wagtail note: title/date/author pulled from page model fields.
    """
    header_style = ChoiceBlock(choices=[
        ("standard", "Standard (text only)"),
        ("hero",     "Hero (with featured image)"),
        ("minimal",  "Minimal"),
    ], default="standard", required=False)
    show_featured_image = BooleanBlock(default=True, required=False)
    show_author = BooleanBlock(default=True, required=False)
    show_date = BooleanBlock(default=True, required=False)
    show_tags = BooleanBlock(default=True, required=False)
    content_alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
    ], default="left", required=False)

    class Meta:
        icon = "doc-full"
        label = "Post header"
        template = "cms/blocks/blog_post_header_block.html"


class BlogPostBodyBlock(StructBlock):
    """
    Tonic: tonic-blog-post-body
    The main richtext body of a blog post.
    """
    body = RichTextBlock(
        features=["h2", "h3", "h4", "bold", "italic", "link", "ol", "ul",
                  "blockquote", "image", "embed", "code"],
        label="Post body"
    )
    container_width = ChoiceBlock(choices=[
        ("container-sm", "Narrow (640px)"),
        ("container-md", "Medium (768px)"),
        ("container-lg", "Large (1024px)"),
    ], default="container-sm", required=False)

    class Meta:
        icon = "doc-full-inverse"
        label = "Post body"
        template = "cms/blocks/blog_post_body_block.html"


# ============================================================
# HERO BLOCKS
# ============================================================

class FullHeroBlock(StructBlock):
    """
    Tonic: tonic-full-hero
    Full-width hero section with background image/video, headline, and CTAs.
    """
    eyebrow = CharBlock(max_length=100, required=False, label="Eyebrow label")
    heading = CharBlock(max_length=200, label="Heading")
    heading_tag = ChoiceBlock(choices=[
        ("h1", "H1"), ("h2", "H2"),
    ], default="h1", required=False)
    subheadline = TextBlock(required=False, label="Subheadline")
    primary_cta = ButtonBlock(required=False, label="Primary CTA")
    secondary_cta = ButtonBlock(required=False, label="Secondary CTA")
    background_image = ImageChooserBlock(required=False, label="Background image")
    video_url = URLBlock(required=False, label="Background video URL (MP4)")
    background_type = ChoiceBlock(choices=[
        ("light",   "Light"),
        ("dark",    "Dark"),
        ("primary", "Brand primary"),
        ("image",   "Background image"),
        ("video",   "Background video"),
    ], default="dark", required=False)
    hero_height = ChoiceBlock(choices=[
        ("auto",    "Auto (content height)"),
        ("medium",  "Medium (60vh)"),
        ("large",   "Large (80vh)"),
        ("full",    "Full screen (100vh)"),
    ], default="large", required=False)
    content_alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
    ], default="center", required=False)

    class Meta:
        icon = "image"
        label = "Full-width hero"
        template = "cms/blocks/full_hero_block.html"


class SplitHeroBlock(StructBlock):
    """
    Tonic: tonic-split-hero
    Two-column hero: text left, media right (or reversed).
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, label="Heading")
    heading_tag = ChoiceBlock(choices=[
        ("h1", "H1"), ("h2", "H2"),
    ], default="h1", required=False)
    subheadline = TextBlock(required=False)
    primary_cta = ButtonBlock(required=False, label="Primary CTA")
    secondary_cta = ButtonBlock(required=False, label="Secondary CTA")
    media_type = ChoiceBlock(choices=[
        ("image", "Image"),
        ("video", "Video"),
        ("embed", "Embed"),
    ], default="image", required=False)
    image = ImageChooserBlock(required=False)
    video_url = URLBlock(required=False, label="Video URL (MP4 or YouTube)")
    embed_url = URLBlock(required=False, label="Embed URL")
    media_side = ChoiceBlock(choices=[
        ("right", "Right"),
        ("left",  "Left"),
    ], default="right", required=False)
    split_ratio = ChoiceBlock(choices=[
        ("50-50", "50 / 50"),
        ("40-60", "40 / 60"),
        ("60-40", "60 / 40"),
    ], default="50-50", required=False)
    background_type = ChoiceBlock(choices=[
        ("light", "Light"),
        ("dark",  "Dark"),
        ("alt",   "Alternate"),
    ], default="light", required=False)

    class Meta:
        icon = "image"
        label = "Split hero"
        template = "cms/blocks/split_hero_block.html"


class VideoBannerBlock(StructBlock):
    """
    Tonic: tonic-video-banner
    Full-width background video with text overlay and CTAs.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, label="Heading")
    heading_tag = ChoiceBlock(choices=[
        ("h1", "H1"), ("h2", "H2"),
    ], default="h2", required=False)
    subheadline = TextBlock(required=False)
    primary_cta = ButtonBlock(required=False, label="Primary CTA")
    secondary_cta = ButtonBlock(required=False, label="Secondary CTA")
    video_source = ChoiceBlock(choices=[
        ("mp4",     "Self-hosted MP4"),
        ("youtube", "YouTube"),
        ("vimeo",   "Vimeo"),
    ], default="mp4", required=False)
    mp4_url = URLBlock(required=False, label="MP4 video URL")
    youtube_url = URLBlock(required=False, label="YouTube URL")
    vimeo_url = URLBlock(required=False, label="Vimeo URL")
    fallback_image = ImageChooserBlock(required=False, label="Fallback image (mobile)")
    autoplay = BooleanBlock(default=True, required=False)
    muted = BooleanBlock(default=True, required=False)
    loop = BooleanBlock(default=True, required=False)
    content_alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
    ], default="center", required=False)

    class Meta:
        icon = "media"
        label = "Video banner"
        template = "cms/blocks/video_banner_block.html"


# ============================================================
# CONTENT BLOCKS
# ============================================================

class RichTextSectionBlock(StructBlock):
    """
    Tonic: tonic-richtext
    Standalone rich text content section.
    """
    rich_text = RichTextBlock(
        features=["h2", "h3", "h4", "bold", "italic", "link", "ol", "ul",
                  "blockquote", "image", "embed", "code"],
        label="Content"
    )
    container_width = ChoiceBlock(choices=[
        ("container-sm",  "Narrow reading width (640px)"),
        ("container-md",  "Medium (768px)"),
        ("container-lg",  "Large (1024px)"),
        ("container-xl",  "Full width (1280px)"),
    ], default="container-md", required=False)
    text_alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
    ], default="left", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "pilcrow"
        label = "Rich text"
        template = "cms/blocks/rich_text_section_block.html"


class SectionHeaderModuleBlock(StructBlock):
    """
    Tonic: tonic-section-header
    Standalone centered section header with optional CTAs.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, label="Heading")
    heading_level = ChoiceBlock(choices=[
        ("h1", "H1"), ("h2", "H2"), ("h3", "H3"),
    ], default="h2", required=False)
    subheading = TextBlock(required=False)
    primary_cta = ButtonBlock(required=False)
    secondary_cta = ButtonBlock(required=False)
    text_alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
    ], default="center", required=False)
    background = BackgroundBlock(required=False)
    show_divider = BooleanBlock(default=False, required=False, label="Show decorative divider")

    class Meta:
        icon = "title"
        label = "Section header"
        template = "cms/blocks/section_header_module_block.html"


class ImageTextBlock(StructBlock):
    """
    Tonic: tonic-image-text
    Two-column section with image on one side, text on the other.
    """
    image = ImageChooserBlock(label="Image")
    image_caption = CharBlock(max_length=200, required=False, label="Caption")
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    heading_level = ChoiceBlock(choices=[
        ("h2", "H2"), ("h3", "H3"),
    ], default="h2", required=False)
    body = RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul", "blockquote"],
        required=False
    )
    primary_cta = ButtonBlock(required=False)
    secondary_cta = ButtonBlock(required=False)
    image_side = ChoiceBlock(choices=[
        ("left",  "Image left"),
        ("right", "Image right"),
    ], default="right", required=False)
    column_split = ChoiceBlock(choices=[
        ("50-50", "50 / 50"),
        ("40-60", "40 / 60 (text wider)"),
        ("60-40", "60 / 40 (image wider)"),
    ], default="50-50", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "image"
        label = "Image + text"
        template = "cms/blocks/image_text_block.html"


class ImageFigureBlock(StructBlock):
    """
    Tonic: tonic-image
    Standalone image with optional caption and link.
    """
    image = ImageChooserBlock(label="Image")
    show_caption = BooleanBlock(default=False, required=False)
    caption = CharBlock(max_length=300, required=False)
    link_image = BooleanBlock(default=False, required=False, label="Link the image")
    image_link = URLBlock(required=False, label="Image link URL")
    alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
        ("right",  "Right"),
    ], default="center", required=False)
    container_width = ChoiceBlock(choices=[
        ("container-sm", "Narrow"),
        ("container-md", "Medium"),
        ("container-lg", "Large"),
        ("container-xl", "Full width"),
    ], default="container-lg", required=False)

    class Meta:
        icon = "image"
        label = "Image figure"
        template = "cms/blocks/image_figure_block.html"


class EmbedSectionBlock(StructBlock):
    """
    Tonic: tonic-embed
    Embeds an iframe (YouTube, Vimeo, map, form, etc.) with a ratio box.
    """
    embed_url = URLBlock(label="Embed URL")
    embed_title = CharBlock(max_length=200, required=False, label="Accessibility title")
    show_caption = BooleanBlock(default=False, required=False)
    caption = CharBlock(max_length=300, required=False)
    aspect_ratio = ChoiceBlock(choices=[
        ("16-9",  "16:9 (video)"),
        ("4-3",   "4:3"),
        ("1-1",   "1:1 (square)"),
        ("fixed", "Fixed height"),
    ], default="16-9", required=False)
    fixed_height = IntegerBlock(
        default=400, required=False,
        help_text="Height in px (only used when aspect ratio is Fixed)"
    )
    alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
        ("right",  "Right"),
    ], default="center", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "media"
        label = "Embed"
        template = "cms/blocks/embed_section_block.html"


class VideoEmbedBlock(StructBlock):
    """
    Tonic: tonic-video
    Video embed with thumbnail play button and optional heading.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    video_type = ChoiceBlock(choices=[
        ("youtube",  "YouTube"),
        ("vimeo",    "Vimeo"),
        ("external", "External URL"),
    ], default="youtube", required=False)
    video_url = URLBlock(label="Video URL")
    custom_thumbnail = ImageChooserBlock(required=False, label="Custom thumbnail")
    caption = CharBlock(max_length=300, required=False)
    autoplay = BooleanBlock(default=False, required=False)
    loop = BooleanBlock(default=False, required=False)
    aspect_ratio = ChoiceBlock(choices=[
        ("16-9", "16:9"),
        ("4-3",  "4:3"),
        ("1-1",  "1:1"),
    ], default="16-9", required=False)
    container_width = ChoiceBlock(choices=[
        ("container-sm", "Narrow"),
        ("container-md", "Medium"),
        ("container-lg", "Large"),
        ("container-xl", "Full width"),
    ], default="container-lg", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "media"
        label = "Video"
        template = "cms/blocks/video_embed_block.html"


class CodeBlock(StructBlock):
    """
    Tonic: tonic-code
    Syntax-highlighted code block (uses Prism.js in template).
    """
    code_snippet = TextBlock(label="Code")
    language = ChoiceBlock(choices=[
        ("markup",     "HTML"),
        ("css",        "CSS"),
        ("javascript", "JavaScript"),
        ("python",     "Python"),
        ("bash",       "Bash / Shell"),
        ("json",       "JSON"),
        ("sql",        "SQL"),
        ("typescript", "TypeScript"),
        ("django",     "Django template"),
        ("none",       "Plain text"),
    ], default="python", required=False)
    caption = CharBlock(max_length=200, required=False)
    show_line_numbers = BooleanBlock(default=True, required=False)

    class Meta:
        icon = "code"
        label = "Code block"
        template = "cms/blocks/code_block.html"


# ============================================================
# MARKETING / CTA BLOCKS
# ============================================================

class CTABannerBlock(StructBlock):
    """
    Tonic: tonic-cta-banner
    Full-width CTA section with headline, subheading, and buttons.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, label="Heading")
    heading_level = ChoiceBlock(choices=[
        ("h2", "H2"), ("h3", "H3"),
    ], default="h2", required=False)
    subheading = TextBlock(required=False)
    primary_cta = ButtonBlock(required=False, label="Primary button")
    secondary_cta = ButtonBlock(required=False, label="Secondary button")
    layout = ChoiceBlock(choices=[
        ("centered",      "Centered"),
        ("left",          "Left aligned"),
        ("split",         "Split (text left, buttons right)"),
    ], default="centered", required=False)
    background = BackgroundBlock(required=False)
    background_image = ImageChooserBlock(required=False)

    class Meta:
        icon = "mail"
        label = "CTA banner"
        template = "cms/blocks/cta_banner_block.html"


class SplitCTABlock(StructBlock):
    """
    Tonic: tonic-split-cta
    Two-column CTA: copy left, form or content right.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, label="Heading")
    heading_level = ChoiceBlock(choices=[
        ("h2", "H2"), ("h3", "H3"),
    ], default="h2", required=False)
    body = RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul"],
        required=False,
        label="Body copy"
    )
    cta_link_text = CharBlock(max_length=100, required=False, label="Link text")
    cta_link_url = URLBlock(required=False, label="Link URL")
    form_heading = CharBlock(max_length=200, required=False, label="Form heading")
    right_content = RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul", "blockquote"],
        required=False,
        label="Right column content (if no form)"
    )
    copy_side = ChoiceBlock(choices=[
        ("left",  "Copy left, form right"),
        ("right", "Form left, copy right"),
    ], default="left", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "form"
        label = "Split CTA"
        template = "cms/blocks/split_cta_block.html"


class AnnouncementBarBlock(StructBlock):
    """
    Tonic: tonic-announcements
    Slim announcement bar for top-of-page notices.
    """
    message_text = CharBlock(max_length=300, label="Message")
    show_cta = BooleanBlock(default=False, required=False, label="Show CTA button")
    cta_label = CharBlock(max_length=80, required=False, label="CTA label")
    cta_url = URLBlock(required=False, label="CTA URL")
    scroll_mode = ChoiceBlock(choices=[
        ("static",  "Static"),
        ("marquee", "Scrolling marquee"),
    ], default="static", required=False)

    class Meta:
        icon = "warning"
        label = "Announcement bar"
        template = "cms/blocks/announcement_bar_block.html"


# ============================================================
# FEATURE / GRID BLOCKS
# ============================================================

class FeatureItem(StructBlock):
    icon = CharBlock(max_length=80, required=False, help_text="Emoji or CSS icon class")
    title = CharBlock(max_length=150)
    description = RichTextBlock(
        features=["bold", "italic", "link"],
        required=False
    )
    link_text = CharBlock(max_length=80, required=False)
    link_url = URLBlock(required=False)


class FeatureListBlock(StructBlock):
    """
    Tonic: tonic-features-list
    List of features with icons, titles, descriptions, and optional links.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subheading = RichTextBlock(features=["bold", "italic"], required=False)
    items = ListBlock(FeatureItem(), label="Feature items")
    item_layout = ChoiceBlock(choices=[
        ("icon-top",  "Icon above text"),
        ("icon-left", "Icon left of text"),
    ], default="icon-top", required=False)
    columns_desktop = ChoiceBlock(choices=[
        ("1", "1 column"),
        ("2", "2 columns"),
        ("3", "3 columns"),
        ("4", "4 columns"),
    ], default="3", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "list-ul"
        label = "Feature list"
        template = "cms/blocks/feature_list_block.html"


class IconFeatureItem(StructBlock):
    icon = CharBlock(max_length=80, required=False, help_text="Emoji or CSS icon class")
    title = CharBlock(max_length=150)
    description = RichTextBlock(features=["bold", "italic", "link"], required=False)


class IconFeatureGridBlock(StructBlock):
    """
    Tonic: tonic-icon-feature-grid
    Grid of icon + title + description feature cards.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subtext = RichTextBlock(features=["bold", "italic"], required=False)
    items = ListBlock(IconFeatureItem(), label="Features")
    columns_desktop = ChoiceBlock(choices=[
        ("2", "2 columns"),
        ("3", "3 columns"),
        ("4", "4 columns"),
    ], default="3", required=False)
    item_layout = ChoiceBlock(choices=[
        ("top",  "Icon above"),
        ("left", "Icon left"),
    ], default="top", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "grip"
        label = "Icon feature grid"
        template = "cms/blocks/icon_feature_grid_block.html"


class CardItem(StructBlock):
    media_type = ChoiceBlock(choices=[
        ("image", "Image"),
        ("icon",  "Icon"),
        ("none",  "None"),
    ], default="image", required=False)
    image = ImageChooserBlock(required=False)
    icon = CharBlock(max_length=80, required=False, help_text="Emoji or CSS icon class")
    eyebrow = CharBlock(max_length=100, required=False)
    title = CharBlock(max_length=200)
    description = RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul"],
        required=False
    )
    button_label = CharBlock(max_length=80, required=False)
    button_url = URLBlock(required=False)
    button_style = ChoiceBlock(choices=[
        ("primary",   "Primary"),
        ("secondary", "Secondary"),
        ("ghost",     "Ghost"),
        ("subtle",    "Subtle"),
        ("link",      "Link"),
    ], default="primary", required=False)


class CardsBlock(StructBlock):
    """
    Tonic: tonic-cards
    Repeater of content cards with image/icon, title, description, and CTA.
    """
    cards = ListBlock(CardItem(), label="Cards")
    media_position = ChoiceBlock(choices=[
        ("top",    "Media top"),
        ("bottom", "Media bottom"),
        ("left",   "Media left"),
        ("right",  "Media right"),
    ], default="top", required=False)
    columns_desktop = ChoiceBlock(choices=[
        ("1", "1 column"),
        ("2", "2 columns"),
        ("3", "3 columns"),
        ("4", "4 columns"),
    ], default="3", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "grip"
        label = "Cards"
        template = "cms/blocks/cards_block.html"


# ============================================================
# SOCIAL PROOF BLOCKS
# ============================================================

class TestimonialItem(StructBlock):
    star_rating = ChoiceBlock(choices=[
        ("0", "No stars"),
        ("3", "3 stars"),
        ("4", "4 stars"),
        ("5", "5 stars"),
    ], default="5", required=False)
    quote = TextBlock(label="Quote")
    author_name = CharBlock(max_length=120)
    author_title = CharBlock(max_length=120, required=False)
    company_name = CharBlock(max_length=120, required=False)
    avatar = ImageChooserBlock(required=False)
    company_logo = ImageChooserBlock(required=False)


class TestimonialsGridBlock(StructBlock):
    """
    Tonic: tonic-testimonials-grid
    Grid of testimonial cards.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subheading = TextBlock(required=False)
    testimonials = ListBlock(TestimonialItem(), label="Testimonials")
    columns_desktop = ChoiceBlock(choices=[
        ("1", "1 column"),
        ("2", "2 columns"),
        ("3", "3 columns"),
    ], default="3", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "openquote"
        label = "Testimonials grid"
        template = "cms/blocks/testimonials_grid_block.html"


class TestimonialsSliderBlock(StructBlock):
    """
    Tonic: tonic-testimonials-slider
    Carousel of testimonial cards.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subheading = TextBlock(required=False)
    testimonials = ListBlock(TestimonialItem(), label="Testimonials")
    slides_to_show = ChoiceBlock(choices=[
        ("1", "1 at a time"),
        ("2", "2 at a time"),
        ("3", "3 at a time"),
    ], default="3", required=False)
    autoplay = BooleanBlock(default=False, required=False)
    autoplay_delay = IntegerBlock(default=4000, required=False, label="Autoplay delay (ms)")
    show_arrows = BooleanBlock(default=True, required=False)
    show_dots = BooleanBlock(default=True, required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "openquote"
        label = "Testimonials slider"
        template = "cms/blocks/testimonials_slider_block.html"


class LogoItem(StructBlock):
    logo_image = ImageChooserBlock(label="Logo")
    company_name = CharBlock(max_length=120, required=False, label="Company name (alt text)")
    link_url = URLBlock(required=False, label="Link URL")


class LogoGridBlock(StructBlock):
    """
    Tonic: tonic-logos-scroller
    Trust bar of client/partner logos, static grid or marquee scroll.
    """
    eyebrow = CharBlock(max_length=100, required=False, label="Eyebrow label")
    logos = ListBlock(LogoItem(), label="Logos")
    display_mode = ChoiceBlock(choices=[
        ("grid",    "Static grid"),
        ("marquee", "Scrolling marquee"),
    ], default="grid", required=False)
    columns_desktop = ChoiceBlock(choices=[
        ("3", "3 columns"),
        ("4", "4 columns"),
        ("5", "5 columns"),
        ("6", "6 columns"),
    ], default="5", required=False)
    scroll_direction = ChoiceBlock(choices=[
        ("left",  "Left"),
        ("right", "Right"),
    ], default="left", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "image"
        label = "Logo grid"
        template = "cms/blocks/logo_grid_block.html"


class StatItem(StructBlock):
    prefix = CharBlock(max_length=20, required=False, help_text="e.g. $")
    number = CharBlock(max_length=20, label="Number", help_text="e.g. 10,000 or 98")
    suffix = CharBlock(max_length=20, required=False, help_text="e.g. + or %")
    stat_label = CharBlock(max_length=120, label="Label")
    description = CharBlock(max_length=255, required=False)


class StatsBlock(StructBlock):
    """
    Tonic: tonic-stats-numbers
    Row of key statistics / numbers with optional count-up animation.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subheading = TextBlock(required=False)
    stats = ListBlock(StatItem(), label="Stats")
    columns_desktop = ChoiceBlock(choices=[
        ("2", "2 columns"),
        ("3", "3 columns"),
        ("4", "4 columns"),
    ], default="3", required=False)
    show_dividers = BooleanBlock(default=False, required=False)
    show_card_style = BooleanBlock(default=False, required=False, label="Card background")
    enable_countup = BooleanBlock(default=True, required=False, label="Count-up animation")
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "pick"
        label = "Stats / numbers"
        template = "cms/blocks/stats_block.html"


# ============================================================
# NAVIGATION / UX BLOCKS
# ============================================================

class FAQItem(StructBlock):
    question = CharBlock(max_length=300, label="Question")
    answer = RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul"],
        label="Answer"
    )
    open_by_default = BooleanBlock(default=False, required=False)


class FAQBlock(StructBlock):
    """
    Tonic: tonic-faq
    Accordion FAQ section with optional FAQ schema markup support.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subtext = RichTextBlock(features=["bold", "italic", "link"], required=False)
    items = ListBlock(FAQItem(), label="FAQ items")
    item_style = ChoiceBlock(choices=[
        ("minimal", "Minimal (dividers only)"),
        ("boxed",   "Boxed"),
        ("filled",  "Filled"),
    ], default="minimal", required=False)
    icon_type = ChoiceBlock(choices=[
        ("chevron",   "Chevron"),
        ("plus_minus", "Plus / Minus"),
    ], default="chevron", required=False)
    allow_multiple_open = BooleanBlock(default=False, required=False)
    enable_faq_schema = BooleanBlock(
        default=True,
        required=False,
        label="Enable FAQ schema markup",
        help_text="Adds JSON-LD structured data for Google rich results"
    )
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "help"
        label = "FAQ accordion"
        template = "cms/blocks/faq_block.html"


class BreadcrumbItem(StructBlock):
    label = CharBlock(max_length=120)
    url = URLBlock(required=False)


class BreadcrumbsBlock(StructBlock):
    """
    Tonic: tonic-breadcrumbs
    Manual breadcrumb trail. For auto-breadcrumbs use a context processor instead.
    """
    show_home = BooleanBlock(default=True, required=False)
    home_label = CharBlock(max_length=60, default="Home", required=False)
    crumbs = ListBlock(BreadcrumbItem(), label="Crumbs", required=False)
    current_page_label = CharBlock(max_length=200, required=False,
                                   help_text="Leave blank to use current page title")
    separator = ChoiceBlock(choices=[
        ("slash",   "/ slash"),
        ("chevron", "> chevron"),
        ("dot",     "· dot"),
        ("arrow",   "→ arrow"),
    ], default="slash", required=False)
    text_size = ChoiceBlock(choices=[
        ("sm",   "Small"),
        ("base", "Base"),
        ("lg",   "Large"),
    ], default="sm", required=False)

    class Meta:
        icon = "breadcrumb-expand"
        label = "Breadcrumbs"
        template = "cms/blocks/breadcrumbs_block.html"


class TabItem(StructBlock):
    tab_label = CharBlock(max_length=120, label="Tab label")
    tab_content = RichTextBlock(
        features=["h3", "h4", "bold", "italic", "link", "ol", "ul",
                  "blockquote", "image"],
        label="Tab content"
    )


class TabsPanelsBlock(StructBlock):
    """
    Tonic: tonic-tabs-and-panels
    Tabbed content area with multiple panels.
    """
    section_eyebrow = CharBlock(max_length=100, required=False)
    section_heading = CharBlock(max_length=200, required=False)
    section_subtext = TextBlock(required=False)
    tabs = ListBlock(TabItem(), label="Tabs")
    tab_style = ChoiceBlock(choices=[
        ("underline", "Underline"),
        ("pill",      "Pill"),
        ("boxed",     "Boxed"),
    ], default="underline", required=False)
    tab_orientation = ChoiceBlock(choices=[
        ("top",  "Tabs on top"),
        ("left", "Tabs on left"),
    ], default="top", required=False)
    mobile_behavior = ChoiceBlock(choices=[
        ("scroll",   "Scrollable tab strip"),
        ("accordion", "Accordion"),
    ], default="scroll", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "list-ol"
        label = "Tabs and panels"
        template = "cms/blocks/tabs_panels_block.html"


class ButtonGroupBlock(StructBlock):
    """
    Tonic: tonic-button
    Standalone group of one or more buttons.
    """
    buttons = ListBlock(ButtonBlock(), label="Buttons")
    alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
        ("right",  "Right"),
    ], default="left", required=False)
    layout = ChoiceBlock(choices=[
        ("inline", "Inline (side by side)"),
        ("stacked", "Stacked"),
    ], default="inline", required=False)

    class Meta:
        icon = "link"
        label = "Button group"
        template = "cms/blocks/button_group_block.html"


# ============================================================
# MEDIA / GALLERY BLOCKS
# ============================================================

class GalleryImage(StructBlock):
    image = ImageChooserBlock()
    caption = CharBlock(max_length=300, required=False)
    link_url = URLBlock(required=False, label="Link URL")


class ImageGalleryBlock(StructBlock):
    """
    Tonic: tonic-image-gallery
    Responsive image grid or masonry gallery with optional lightbox.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subheading = TextBlock(required=False)
    images = ListBlock(GalleryImage(), label="Images")
    layout = ChoiceBlock(choices=[
        ("grid",    "Grid"),
        ("masonry", "Masonry"),
    ], default="grid", required=False)
    columns_desktop = ChoiceBlock(choices=[
        ("2", "2 columns"),
        ("3", "3 columns"),
        ("4", "4 columns"),
    ], default="3", required=False)
    aspect_ratio = ChoiceBlock(choices=[
        ("1-1",  "Square 1:1"),
        ("4-3",  "4:3"),
        ("16-9", "16:9"),
        ("3-4",  "Portrait 3:4"),
    ], default="4-3", required=False)
    enable_lightbox = BooleanBlock(default=True, required=False)
    show_caption_overlay = BooleanBlock(default=False, required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "image"
        label = "Image gallery"
        template = "cms/blocks/image_gallery_block.html"


class SlideItem(StructBlock):
    image = ImageChooserBlock(required=False, label="Slide image")
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    description = TextBlock(required=False)
    cta_text = CharBlock(max_length=80, required=False)
    cta_url = URLBlock(required=False)


class SliderBlock(StructBlock):
    """
    Tonic: tonic-slider
    Image/content carousel with arrow and dot controls.
    """
    slides = ListBlock(SlideItem(), label="Slides")
    slides_to_show = ChoiceBlock(choices=[
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
    ], default="1", required=False)
    autoplay = BooleanBlock(default=False, required=False)
    autoplay_speed = IntegerBlock(default=4000, required=False, label="Autoplay speed (ms)")
    loop = BooleanBlock(default=True, required=False)
    show_arrows = BooleanBlock(default=True, required=False)
    arrow_position = ChoiceBlock(choices=[
        ("sides",  "Sides"),
        ("above",  "Above"),
        ("below",  "Below"),
    ], default="sides", required=False)
    show_dots = BooleanBlock(default=True, required=False)
    slide_height = ChoiceBlock(choices=[
        ("auto",   "Auto"),
        ("medium", "Medium (400px)"),
        ("large",  "Large (560px)"),
        ("full",   "Full screen"),
    ], default="medium", required=False)

    class Meta:
        icon = "image"
        label = "Image slider"
        template = "cms/blocks/slider_block.html"


# ============================================================
# TEAM / PEOPLE BLOCKS
# ============================================================

class TeamMemberItem(StructBlock):
    photo = ImageChooserBlock(required=False)
    name = CharBlock(max_length=120, label="Name")
    job_title = CharBlock(max_length=120, required=False)
    bio = RichTextBlock(
        features=["bold", "italic", "link"],
        required=False
    )
    linkedin = URLBlock(required=False, label="LinkedIn URL")
    twitter = URLBlock(required=False, label="Twitter/X URL")
    instagram = URLBlock(required=False, label="Instagram URL")
    website = URLBlock(required=False, label="Website URL")


class TeamGridBlock(StructBlock):
    """
    Tonic: tonic-team-grid
    Grid of team member cards with photos, titles, bios, and social links.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subtext = RichTextBlock(features=["bold", "italic"], required=False)
    members = ListBlock(TeamMemberItem(), label="Team members")
    columns_desktop = ChoiceBlock(choices=[
        ("2", "2 columns"),
        ("3", "3 columns"),
        ("4", "4 columns"),
    ], default="4", required=False)
    photo_shape = ChoiceBlock(choices=[
        ("square",  "Square"),
        ("circle",  "Circle"),
        ("rounded", "Rounded"),
    ], default="square", required=False)
    text_alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
    ], default="center", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "group"
        label = "Team grid"
        template = "cms/blocks/team_grid_block.html"


# ============================================================
# CONTACT / UTILITY BLOCKS
# ============================================================

class ContactInfoBlock(StructBlock):
    """
    Tonic: tonic-contact-info
    Structured contact information display (address, phone, email, hours).
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subheading = TextBlock(required=False)

    show_address = BooleanBlock(default=True, required=False)
    street = CharBlock(max_length=200, required=False, label="Street address")
    city_state_zip = CharBlock(max_length=200, required=False, label="City, state, zip")
    country = CharBlock(max_length=100, required=False)
    directions_text = CharBlock(max_length=80, required=False, default="Get directions")
    directions_url = URLBlock(required=False, label="Directions URL")

    show_phone = BooleanBlock(default=True, required=False)
    primary_number = CharBlock(max_length=30, required=False, label="Primary phone")
    secondary_number = CharBlock(max_length=30, required=False, label="Secondary phone")

    show_email = BooleanBlock(default=True, required=False)
    primary_email = CharBlock(max_length=200, required=False, label="Primary email")
    secondary_email = CharBlock(max_length=200, required=False, label="Secondary email")

    show_hours = BooleanBlock(default=True, required=False)
    hours_text = RichTextBlock(
        features=["bold", "italic"],
        required=False,
        label="Hours of operation"
    )

    columns = ChoiceBlock(choices=[
        ("1", "1 column"),
        ("2", "2 columns"),
    ], default="2", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "site"
        label = "Contact info"
        template = "cms/blocks/contact_info_block.html"


class MapEmbedBlock(StructBlock):
    """
    Tonic: tonic-map-embed
    Google Maps embed with optional location list.
    Wagtail note: API key should be stored in settings, not per-block.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subheading = TextBlock(required=False)
    embed_url = URLBlock(
        required=False,
        label="Map embed URL",
        help_text="Google Maps embed URL (iframe src)"
    )
    map_height = IntegerBlock(default=450, label="Map height (px)")
    show_location_list = BooleanBlock(default=False, required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "site"
        label = "Map embed"
        template = "cms/blocks/map_embed_block.html"


class CountdownTimerBlock(StructBlock):
    """
    Tonic: tonic-countdown-timer
    Countdown to a target date/time.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subheading = TextBlock(required=False)
    target_date = CharBlock(
        max_length=20,
        label="Target date",
        help_text="Format: YYYY-MM-DD"
    )
    target_time = CharBlock(
        max_length=10,
        default="00:00",
        required=False,
        label="Target time (HH:MM)"
    )
    expired_heading = CharBlock(max_length=200, required=False, default="Event has ended")
    expired_message = CharBlock(max_length=300, required=False)
    show_cta = BooleanBlock(default=False, required=False, label="Show CTA after countdown")
    cta_text = CharBlock(max_length=80, required=False)
    cta_url = URLBlock(required=False)
    label_days = CharBlock(max_length=20, default="Days", required=False)
    label_hours = CharBlock(max_length=20, default="Hours", required=False)
    label_minutes = CharBlock(max_length=20, default="Minutes", required=False)
    label_seconds = CharBlock(max_length=20, default="Seconds", required=False)
    background = BackgroundBlock(required=False)
    background_image = ImageChooserBlock(required=False)

    class Meta:
        icon = "time"
        label = "Countdown timer"
        template = "cms/blocks/countdown_timer_block.html"


# ============================================================
# PROCESS / TIMELINE BLOCKS
# ============================================================

class ProcessStepItem(StructBlock):
    node_type = ChoiceBlock(choices=[
        ("number", "Step number"),
        ("icon",   "Icon"),
        ("dot",    "Dot"),
    ], default="number", required=False)
    icon = CharBlock(max_length=80, required=False, help_text="Emoji or CSS icon class")
    step_title = CharBlock(max_length=150, label="Step title")
    description = RichTextBlock(
        features=["bold", "italic", "link"],
        required=False
    )
    link_text = CharBlock(max_length=80, required=False)
    link_url = URLBlock(required=False)


class ProcessStepsBlock(StructBlock):
    """
    Tonic: tonic-process-steps
    Numbered or icon-based step-by-step process visualization.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subtext = RichTextBlock(features=["bold", "italic"], required=False)
    steps = ListBlock(ProcessStepItem(), label="Steps")
    orientation = ChoiceBlock(choices=[
        ("horizontal", "Horizontal"),
        ("vertical",   "Vertical"),
    ], default="horizontal", required=False)
    columns_desktop = ChoiceBlock(choices=[
        ("2", "2 columns"),
        ("3", "3 columns"),
        ("4", "4 columns"),
    ], default="3", required=False)
    show_connector = BooleanBlock(default=True, required=False, label="Show connector lines")
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "order"
        label = "Process steps"
        template = "cms/blocks/process_steps_block.html"


class TimelineEntryBlock(StructBlock):
    eyebrow = CharBlock(max_length=100, required=False, help_text="e.g. year or date")
    heading = CharBlock(max_length=200)
    description = RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul"],
        required=False
    )
    image = ImageChooserBlock(required=False)
    link_text = CharBlock(max_length=80, required=False)
    link_url = URLBlock(required=False)
    node_style = ChoiceBlock(choices=[
        ("dot",     "Dot"),
        ("ring",    "Ring"),
        ("diamond", "Diamond"),
        ("icon",    "Icon"),
    ], default="dot", required=False)


class TimelineBlock(StructBlock):
    """
    Tonic: tonic-timeline
    Vertical center-spine timeline with alternating left/right entries.
    """
    eyebrow = CharBlock(max_length=100, required=False)
    heading = CharBlock(max_length=200, required=False)
    subheading = TextBlock(required=False)
    items = ListBlock(TimelineEntryBlock(), label="Timeline entries")
    show_connector = BooleanBlock(default=True, required=False)
    show_card = BooleanBlock(default=True, required=False, label="Show card backgrounds")
    header_alignment = ChoiceBlock(choices=[
        ("left",   "Left"),
        ("center", "Center"),
    ], default="center", required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "date"
        label = "Timeline"
        template = "cms/blocks/timeline_block.html"


# ============================================================
# DATA BLOCKS
# ============================================================

class TableCellBlock(StructBlock):
    cell_value = CharBlock(max_length=500, required=False)
    cell_icon = ChoiceBlock(choices=[
        ("none",  "Text only"),
        ("check", "Checkmark"),
        ("x",     "X / cross"),
        ("dash",  "Dash"),
    ], default="none", required=False)


class TableColumnBlock(StructBlock):
    header_text = CharBlock(max_length=200, label="Column header")
    is_featured = BooleanBlock(default=False, required=False, label="Featured column")
    featured_badge = CharBlock(max_length=80, required=False, label="Badge label")


class TableRowBlock(StructBlock):
    row_heading = CharBlock(max_length=200, required=False)
    is_section_break = BooleanBlock(default=False, required=False)
    cells = ListBlock(TableCellBlock(), label="Cells")


class DataTableBlock(StructBlock):
    """
    Tonic: tonic-table
    Comparison or data table with optional featured column and section breaks.
    """
    section_heading = CharBlock(max_length=200, required=False)
    intro_text = TextBlock(required=False)
    columns = ListBlock(TableColumnBlock(), label="Columns")
    rows = ListBlock(TableRowBlock(), label="Rows")
    footnote = TextBlock(required=False)
    striped_rows = BooleanBlock(default=True, required=False)
    sticky_header = BooleanBlock(default=True, required=False)
    background = BackgroundBlock(required=False)

    class Meta:
        icon = "table"
        label = "Data table"
        template = "cms/blocks/data_table_block.html"


# ============================================================
# MAIN CONTENT BLOCK REGISTRY
# ============================================================

CONTENT_BLOCKS = [
    # Heroes
    ("full_hero",          FullHeroBlock()),
    ("split_hero",         SplitHeroBlock()),
    ("video_banner",       VideoBannerBlock()),

    # Core content
    ("rich_text",          RichTextSectionBlock()),
    ("section_header",     SectionHeaderModuleBlock()),
    ("image_text",         ImageTextBlock()),
    ("image_figure",       ImageFigureBlock()),
    ("embed",              EmbedSectionBlock()),
    ("video",              VideoEmbedBlock()),
    ("code_block",         CodeBlock()),

    # Marketing / CTA
    ("cta_banner",         CTABannerBlock()),
    ("split_cta",          SplitCTABlock()),
    ("announcement_bar",   AnnouncementBarBlock()),
    ("button_group",       ButtonGroupBlock()),

    # Features / grids
    ("feature_list",       FeatureListBlock()),
    ("icon_feature_grid",  IconFeatureGridBlock()),
    ("cards",              CardsBlock()),

    # Social proof
    ("testimonials_grid",  TestimonialsGridBlock()),
    ("testimonials_slider",TestimonialsSliderBlock()),
    ("logo_grid",          LogoGridBlock()),
    ("stats",              StatsBlock()),

    # Navigation / UX
    ("faq",                FAQBlock()),
    ("tabs_panels",        TabsPanelsBlock()),
    ("breadcrumbs",        BreadcrumbsBlock()),

    # Media / gallery
    ("image_gallery",      ImageGalleryBlock()),
    ("slider",             SliderBlock()),

    # Team / contact
    ("team_grid",          TeamGridBlock()),
    ("contact_info",       ContactInfoBlock()),
    ("map_embed",          MapEmbedBlock()),
    ("countdown_timer",    CountdownTimerBlock()),

    # Process / timeline
    ("process_steps",      ProcessStepsBlock()),
    ("timeline",           TimelineBlock()),

    # Data
    ("data_table",         DataTableBlock()),

    # Blog (used inside blog page StreamFields)
    ("blog_listing",       BlogListingBlock()),
    ("blog_filter",        BlogFilterBlock()),
    ("blog_pagination",    BlogPaginationBlock()),
    ("blog_related_posts", BlogRelatedPostsBlock()),
    ("blog_toc",           BlogTOCBlock()),
    ("blog_author_box",    BlogAuthorBoxBlock()),
    ("blog_post_header",   BlogPostHeaderBlock()),
    ("blog_post_body",     BlogPostBodyBlock()),
]