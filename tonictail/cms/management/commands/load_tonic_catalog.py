"""
Management command: load_tonic_catalog
Usage: python manage.py load_tonic_catalog [--reset]

Creates the full Tonic theme catalog and documentation site.
This is the production content load for tonictail.com/tonic —
a brochure and reference site for the Tonic HubSpot theme.

Safe to re-run — checks for existing pages before creating.
Use --reset to wipe and rebuild from scratch.

Author: Jonathan Sumner | jonathan@khaoticdigital.com
Theme: Tonic — Khaotic Digital, LLC
"""

import json
import uuid

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wagtail.models import Page, Site

User = get_user_model()


# ============================================================
# STREAM FIELD HELPERS  (identical API to load_demo.py)
# ============================================================

def block(block_type, value):
    return {"type": block_type, "value": value, "id": str(uuid.uuid4())}


def btn(label, url="/", style="primary", size="md"):
    return {"label": label, "url": url, "style": style, "size": size, "open_in_new_tab": False}


def background(bg_type="light"):
    return {"background_type": bg_type}


def rich(html):
    return html


# ============================================================
# BLOCK SHORTCUTS
# ============================================================

def hero_full(heading, subheadline, eyebrow="", primary_label="", primary_url="/",
              secondary_label="", secondary_url="#", bg_type="dark"):
    return block("full_hero", {
        "eyebrow": eyebrow,
        "heading": heading,
        "heading_tag": "h1",
        "subheadline": subheadline,
        "primary_cta": btn(primary_label, primary_url, "primary", "lg") if primary_label else btn("", ""),
        "secondary_cta": btn(secondary_label, secondary_url, "ghost", "lg") if secondary_label else btn("", ""),
        "background_type": bg_type,
        "background_image": None,
        "video_url": "",
        "hero_height": "large",
        "content_alignment": "center",
    })


def split_hero(heading, subheadline, eyebrow="", primary_label="", primary_url="",
               secondary_label="", secondary_url="", media_side="right", bg_type="light"):
    return block("split_hero", {
        "eyebrow": eyebrow,
        "heading": heading,
        "heading_tag": "h1",
        "subheadline": subheadline,
        "primary_cta": btn(primary_label, primary_url) if primary_label else btn("", ""),
        "secondary_cta": btn(secondary_label, secondary_url, "ghost") if secondary_label else btn("", ""),
        "media_type": "image",
        "image": None,
        "video_url": "",
        "embed_url": "",
        "media_side": media_side,
        "split_ratio": "50-50",
        "background_type": bg_type,
    })


def section_header(heading, subheading="", eyebrow="", alignment="center", bg_type="light", show_divider=False):
    return block("section_header", {
        "eyebrow": eyebrow,
        "heading": heading,
        "heading_level": "h2",
        "subheading": subheading,
        "primary_cta": btn("", ""),
        "secondary_cta": btn("", ""),
        "text_alignment": alignment,
        "background": background(bg_type),
        "show_divider": show_divider,
    })


def icon_feature_grid(eyebrow, heading, subtext, items, bg_type="light", columns="3"):
    return block("icon_feature_grid", {
        "eyebrow": eyebrow,
        "heading": heading,
        "subtext": rich(f"<p>{subtext}</p>"),
        "items": items,
        "columns_desktop": columns,
        "item_layout": "top",
        "background": background(bg_type),
    })


def icon_item(icon, title, description):
    return {"icon": icon, "title": title, "description": rich(f"<p>{description}</p>")}


def stats_row(eyebrow, heading, stats_list, bg_type="light", columns="4", dividers=True):
    return block("stats", {
        "eyebrow": eyebrow,
        "heading": heading,
        "subheading": "",
        "stats": stats_list,
        "columns_desktop": columns,
        "show_dividers": dividers,
        "show_card_style": False,
        "enable_countup": True,
        "background": background(bg_type),
    })


def stat(number, label, prefix="", suffix="", description=""):
    return {"prefix": prefix, "number": number, "suffix": suffix,
            "stat_label": label, "description": description}


def cta_banner(heading, subheading, primary_label, primary_url,
               secondary_label="", secondary_url="", bg_type="primary", eyebrow=""):
    return block("cta_banner", {
        "eyebrow": eyebrow,
        "heading": heading,
        "heading_level": "h2",
        "subheading": subheading,
        "primary_cta": btn(primary_label, primary_url, "ghost", "lg"),
        "secondary_cta": btn(secondary_label, secondary_url, "subtle", "lg") if secondary_label else btn("", ""),
        "layout": "centered",
        "background": background(bg_type),
        "background_image": None,
    })


def richtext_block(html, container="container-md", bg_type="light"):
    return block("rich_text", {
        "rich_text": rich(html),
        "container_width": container,
        "text_alignment": "left",
        "background": background(bg_type),
    })


def cards_block(cards, columns="3", bg_type="light"):
    return block("cards", {
        "cards": cards,
        "columns_desktop": columns,
        "media_position": "top",
        "background": background(bg_type),
    })


def card(title, description, eyebrow="", button_label="", button_url="",
         button_style="subtle", icon=""):
    return {
        "media_type": "icon",
        "image": None,
        "icon": icon,
        "eyebrow": eyebrow,
        "title": title,
        "description": rich(f"<p>{description}</p>"),
        "button_label": button_label,
        "button_url": button_url,
        "button_style": button_style,
    }


def faq_block(eyebrow, heading, items, bg_type="light"):
    return block("faq", {
        "eyebrow": eyebrow,
        "heading": heading,
        "subtext": rich(""),
        "items": items,
        "item_style": "minimal",
        "icon_type": "chevron",
        "allow_multiple_open": False,
        "enable_faq_schema": True,
        "background": background(bg_type),
    })


def faq_item(question, answer, open_by_default=False):
    return {
        "question": question,
        "answer": rich(f"<p>{answer}</p>"),
        "open_by_default": open_by_default,
    }


def testimonials_grid(eyebrow, heading, testimonials, bg_type="alt", columns="3"):
    return block("testimonials_grid", {
        "eyebrow": eyebrow,
        "heading": heading,
        "subheading": "",
        "testimonials": testimonials,
        "columns_desktop": columns,
        "background": background(bg_type),
    })


def testimonial(quote, name, title="", company="", stars="5"):
    return {
        "star_rating": stars,
        "quote": quote,
        "author_name": name,
        "author_title": title,
        "company_name": company,
        "avatar": None,
        "company_logo": None,
    }


def process_steps(eyebrow, heading, steps, bg_type="alt", orientation="horizontal", columns="3"):
    return block("process_steps", {
        "eyebrow": eyebrow,
        "heading": heading,
        "subtext": rich(""),
        "steps": steps,
        "orientation": orientation,
        "columns_desktop": columns,
        "show_connector": True,
        "background": background(bg_type),
    })


def step(title, description, node_type="number", icon=""):
    return {
        "node_type": node_type,
        "icon": icon,
        "step_title": title,
        "description": rich(f"<p>{description}</p>"),
        "link_text": "",
        "link_url": "",
    }


def logo_grid(eyebrow, logos, bg_type="alt", columns="5"):
    return block("logo_grid", {
        "eyebrow": eyebrow,
        "logos": logos,
        "display_mode": "grid",
        "columns_desktop": columns,
        "scroll_direction": "left",
        "background": background(bg_type),
    })


def logo(company_name, link_url=""):
    return {"logo_image": None, "company_name": company_name, "link_url": link_url}


def tabs_block(eyebrow, heading, tabs, bg_type="light", style="underline"):
    return block("tabs_panels", {
        "section_eyebrow": eyebrow,
        "section_heading": heading,
        "section_subtext": "",
        "tabs": tabs,
        "tab_style": style,
        "tab_orientation": "top",
        "mobile_behavior": "accordion",
        "background": background(bg_type),
    })


def tab(label, content_html):
    return {"tab_label": label, "tab_content": rich(content_html)}


def announcement_bar(message, cta_label="", cta_url="", scroll_mode="static"):
    return block("announcement_bar", {
        "message_text": message,
        "show_cta": bool(cta_label),
        "cta_label": cta_label,
        "cta_url": cta_url,
        "scroll_mode": scroll_mode,
    })


def timeline_block(eyebrow, heading, items, bg_type="light"):
    return block("timeline", {
        "eyebrow": eyebrow,
        "heading": heading,
        "subtext": rich(""),
        "items": items,
        "background": background(bg_type),
    })


def timeline_item(label, heading, description):
    return {
        "date_label": label,
        "heading": heading,
        "description": rich(f"<p>{description}</p>"),
    }


# ============================================================
# DOCS RICH TEXT HELPER
# Produces the standard DocsPage body list format directly.
# ============================================================

def docs_body(html):
    """Return a StreamField body list for a DocsPage (rich_text only)."""
    return [{"type": "rich_text", "id": str(uuid.uuid4()), "value": html}]


# ============================================================
# PAGE CONTENT: HOMEPAGE
# ============================================================

def home_page_content():
    return json.dumps([
        announcement_bar(
            "✨ Tonic v1.1 is here — Forms module, Timeline block, and 12 bug fixes.",
            cta_label="See what's new",
            cta_url="/changelog/",
        ),
        hero_full(
            eyebrow="A HubSpot CMS Theme",
            heading="The last HubSpot theme you'll ever need.",
            subheadline="Tonic is a fully modular HubSpot CMS theme with 34 drag-and-drop modules, a CSS variable design token system, and production-tested templates for every page type.",
            primary_label="Buy on HubSpot Marketplace",
            primary_url="https://ecosystem.hubspot.com",
            secondary_label="Browse the docs",
            secondary_url="/docs/",
            bg_type="dark",
        ),
        logo_grid(
            eyebrow="Used by teams across industries",
            logos=[
                logo("SaaS"), logo("Agency"), logo("eCommerce"),
                logo("Healthcare"), logo("Finance"), logo("Nonprofit"),
            ],
            bg_type="alt",
            columns="6",
        ),
        stats_row(
            eyebrow="By the numbers",
            heading="Built for production, not demos.",
            stats_list=[
                stat("34", "Drag-and-drop modules"),
                stat("6", "Page templates"),
                stat("100", "CSS token variables", suffix="+"),
                stat("0", "Third-party dependencies"),
            ],
            bg_type="light",
            columns="4",
        ),
        icon_feature_grid(
            eyebrow="Why Tonic",
            heading="Every module you need. Nothing you don't.",
            subtext="Tonic was designed around a single principle: a content editor should be able to build any marketing page without touching code.",
            items=[
                icon_item("🎨", "CSS Variable Design System",
                    "Every color, font, spacing value, and border radius is a CSS custom property. Brand your site once in the theme settings panel — all 34 modules update instantly."),
                icon_item("📦", "34 Drag-and-Drop Modules",
                    "Heroes, feature grids, testimonials, sliders, FAQs, forms, stats, timelines, and more. Built as native HubSpot modules with full field editor support."),
                icon_item("📱", "Mobile-First & Accessible",
                    "Every module is responsive by default. Navigation collapses to a hamburger, grids reflow gracefully, and interactive components are keyboard-navigable."),
                icon_item("✍️", "Rich Editor Controls",
                    "Background color, section spacing, heading level, column count, layout variant — content editors control page design without a developer."),
                icon_item("⚡", "Zero External Dependencies",
                    "No Bootstrap, no jQuery, no external CDN calls. Tonic loads fast because it doesn't carry weight it doesn't need."),
                icon_item("🔗", "HubSpot-Native",
                    "Built for HubSpot CMS Hub. Global modules wire to the theme settings. Smart content and personalization tokens work out of the box."),
            ],
            bg_type="light",
        ),
        tabs_block(
            eyebrow="Module categories",
            heading="One theme. Every page type covered.",
            tabs=[
                tab("Heroes & Banners",
                    "<p><strong>Full Hero</strong> — Full-width hero with background image, video, or color. Center or left-aligned content with dual CTAs.</p>"
                    "<p><strong>Split Hero</strong> — 50/50 layout with text and media columns. Supports image, MP4 video, or embed. Column ratio is editor-controlled.</p>"
                    "<p><strong>Video Background Banner</strong> — Autoplay background video with overlay text and CTAs.</p>"
                    "<p><strong>CTA Banner</strong> — Centered or split-layout conversion banner. Ideal for mid-page and bottom-of-page calls to action.</p>"
                    "<p><strong>Split CTA</strong> — Two-column CTA with heading, subtext, and buttons on one side and supporting content on the other.</p>"
                    "<p><strong>Announcement Bar</strong> — Sticky top-of-page bar with static or marquee scroll mode.</p>"),
                tab("Features & Content",
                    "<p><strong>Icon Feature Grid</strong> — Icon, heading, and description cards in a configurable column grid. Supports icon-top and icon-left layouts.</p>"
                    "<p><strong>Feature List</strong> — Checklist-style feature blocks with icon, title, description, and optional link.</p>"
                    "<p><strong>Cards Repeater</strong> — Media-flexible card grid supporting image, icon, or no-media variants. Editor controls column count and card layout.</p>"
                    "<p><strong>Process Steps</strong> — Numbered or icon-driven step sequence with optional connectors. Horizontal and vertical orientations.</p>"
                    "<p><strong>Timeline</strong> — Date-labeled vertical timeline for company history, product roadmaps, or event sequences.</p>"
                    "<p><strong>Section Header</strong> — Standalone eyebrow, heading, subheading, and optional CTA used between content sections.</p>"),
                tab("Social Proof",
                    "<p><strong>Testimonials Grid</strong> — Star-rated quote cards with avatar, author name, title, and company logo. Configurable column count.</p>"
                    "<p><strong>Testimonials Slider</strong> — Auto-advancing carousel of testimonial cards with manual navigation.</p>"
                    "<p><strong>Stats and Numbers</strong> — Animated countup stat display with prefix, suffix, label, and description. Card or inline style.</p>"
                    "<p><strong>Logos Scroller</strong> — Client logo grid or auto-scrolling marquee. Supports linked and unlinked logos.</p>"
                    "<p><strong>Team Grid</strong> — Team member cards with photo, name, title, bio, and social links.</p>"),
                tab("Navigation & Interaction",
                    "<p><strong>FAQ Accordion</strong> — Configurable accordion with chevron or plus-minus icons. Single or multiple open items. Outputs FAQ schema markup.</p>"
                    "<p><strong>Tabbed Content</strong> — Underline, pill, or button-style tab bar with panel content. Collapses to accordion on mobile.</p>"
                    "<p><strong>Breadcrumbs</strong> — Schema-marked breadcrumb trail with configurable separator and custom label override.</p>"
                    "<p><strong>Countdown Timer</strong> — Live days/hours/minutes/seconds display with expired state and optional CTA.</p>"),
                tab("Media & Data",
                    "<p><strong>Image Gallery</strong> — Masonry or grid layout with lightbox. Captions and alt text per image.</p>"
                    "<p><strong>Slider</strong> — Multi-item carousel with autoplay, dots, and arrow navigation. Slide content is editor-built.</p>"
                    "<p><strong>Video</strong> — YouTube, Vimeo, or MP4 embed with poster image and autoplay options.</p>"
                    "<p><strong>Image + Text</strong> — Two-column image and text module with alignment and ratio controls.</p>"
                    "<p><strong>Data Table</strong> — Responsive table with optional header row highlighting and alternating row shading.</p>"
                    "<p><strong>Map Embed</strong> — Google Maps embed with configurable zoom, markers, and map type.</p>"),
                tab("Blog",
                    "<p><strong>Blog Listing</strong> — Main post grid for the blog index. Adapts for tag filters, author pages, and the /all view automatically.</p>"
                    "<p><strong>Blog Filter</strong> — Tag/topic pill bar that generates native HubSpot filter URLs. Active state tracks the current filter.</p>"
                    "<p><strong>Blog Pagination</strong> — Three styles: Numbered, Simple (prev/next), and Minimal (older/newer).</p>"
                    "<p><strong>Blog Post Header</strong> — Global post header with featured image, title, author, date, read time, and topic tags.</p>"
                    "<p><strong>Blog Table of Contents</strong> — Auto-generated TOC from post headings with smooth scroll and active section tracking.</p>"
                    "<p><strong>Blog Author Box</strong> — Author card with avatar, bio, and social links.</p>"
                    "<p><strong>Blog Related Posts</strong> — Content and tag-scored related post grid shown at end of each post.</p>"),
            ],
            bg_type="light",
            style="underline",
        ),
        testimonials_grid(
            eyebrow="What customers say",
            heading="Real teams. Real results.",
            testimonials=[
                testimonial(
                    "We rebranded our entire HubSpot site in a morning. Changed the primary color in theme settings and every module updated. That's not supposed to be that easy.",
                    "Sarah K.", "Marketing Director", "Fintech startup",
                ),
                testimonial(
                    "My client wanted a homepage with a hero, feature grid, testimonials, stats, and a CTA. I built it in under an hour without writing a single line of CSS.",
                    "Marcus D.", "HubSpot Partner", "Digital agency",
                ),
                testimonial(
                    "The FAQ module outputs proper schema markup and the blog TOC is genuinely better than anything I've seen on the marketplace. Worth every dollar.",
                    "Priya N.", "Head of Content", "B2B SaaS",
                ),
            ],
            bg_type="alt",
        ),
        process_steps(
            eyebrow="Getting started",
            heading="Up and running in three steps.",
            steps=[
                step("Purchase the theme",
                    "Buy Tonic from the HubSpot Asset Marketplace. It's instantly available in your HubSpot account."),
                step("Apply to your portal",
                    "Go to Marketing → Files and Templates → Design Tools. Apply the Tonic theme to your portal or to individual pages."),
                step("Customize and publish",
                    "Open Theme Settings to set your brand colors, fonts, and spacing. Build pages with drag-and-drop modules. Publish."),
            ],
            bg_type="light",
        ),
        faq_block(
            eyebrow="FAQ",
            heading="Common questions",
            items=[
                faq_item("What HubSpot subscription do I need?",
                    "Tonic works with HubSpot CMS Hub Starter, Professional, and Enterprise. You need CMS access to install and use themes.",
                    open_by_default=True),
                faq_item("Can my marketing team edit pages without a developer?",
                    "Yes — that's the whole point. Every module is designed for content editors. Background colors, column counts, heading levels, and layout variants are all controlled in the HubSpot page editor without touching code."),
                faq_item("Does Tonic work with HubSpot's smart content and personalization?",
                    "Yes. Tonic modules are native HubSpot modules. Smart content, personalization tokens, A/B testing, and HubSpot's built-in analytics all work as expected."),
                faq_item("How do I update my brand colors across the whole site?",
                    "Open Design Tools → Theme Settings and change the primary, secondary, or accent color. Every Tonic module uses CSS custom properties that inherit those values — the whole site updates on save."),
                faq_item("Is Tonic compatible with the HubSpot blog?",
                    "Yes. Tonic includes seven blog-specific global modules: listing, filter, pagination, post header, post body, table of contents, author box, and related posts. They're all pre-wired to HubSpot's blog template slots."),
                faq_item("Can I use Tonic on multiple HubSpot portals?",
                    "Each purchase covers one HubSpot portal. Contact us if you need a multi-portal or agency license."),
            ],
            bg_type="light",
        ),
        cta_banner(
            heading="Ready to build your best HubSpot site?",
            subheading="Buy Tonic once. Use it forever. Every future update is included.",
            primary_label="Buy on HubSpot Marketplace",
            primary_url="https://ecosystem.hubspot.com",
            secondary_label="Browse the docs",
            secondary_url="/docs/",
            bg_type="primary",
        ),
    ])


# ============================================================
# PAGE CONTENT: MODULES CATALOG
# ============================================================

def modules_page_content():
    """
    Overview catalog page — one card per module category.
    Individual module detail pages live under /docs/modules/.
    """
    return json.dumps([
        section_header(
            eyebrow="Module library",
            heading="34 modules. Every one production-ready.",
            subheading="Every module is a native HubSpot drag-and-drop module with full field editor support. No custom code required.",
            alignment="center",
            bg_type="light",
        ),
        cards_block(
            cards=[
                card("Heroes & Banners", "Full Hero, Split Hero, Video Banner, CTA Banner, Split CTA, Announcement Bar. Six modules for above-the-fold impact.",
                     eyebrow="6 modules", icon="🦸", button_label="View docs", button_url="/docs/modules/heroes/"),
                card("Features & Content", "Icon Feature Grid, Feature List, Cards Repeater, Process Steps, Timeline, Section Header. The core page-building toolkit.",
                     eyebrow="6 modules", icon="📦", button_label="View docs", button_url="/docs/modules/features/"),
                card("Social Proof", "Testimonials Grid, Testimonials Slider, Stats and Numbers, Logos Scroller, Team Grid. Build trust at every scroll depth.",
                     eyebrow="5 modules", icon="⭐", button_label="View docs", button_url="/docs/modules/social-proof/"),
                card("Navigation & Interaction", "FAQ Accordion, Tabbed Content, Breadcrumbs, Countdown Timer. Interactive modules that work without writing JS.",
                     eyebrow="4 modules", icon="🧭", button_label="View docs", button_url="/docs/modules/navigation/"),
                card("Media & Data", "Image Gallery, Slider, Video, Image + Text, Data Table, Map Embed, Image, Rich Text, Embed, Code, List, Button Group, Form.",
                     eyebrow="13 modules", icon="🖼️", button_label="View docs", button_url="/docs/modules/media/"),
                card("Blog System", "Blog Listing, Filter, Pagination, Post Header, Post Body, Table of Contents, Author Box, Related Posts. A complete blog module set.",
                     eyebrow="8 global modules", icon="✍️", button_label="View docs", button_url="/docs/modules/blog/"),
            ],
            columns="3",
            bg_type="alt",
        ),
        section_header(
            eyebrow="Global modules",
            heading="Header, Footer, and Announcement Bar.",
            subheading="Three global modules wire your brand into every page. Edit once — every template updates.",
            alignment="center",
            bg_type="light",
        ),
        icon_feature_grid(
            eyebrow="",
            heading="",
            subtext="",
            items=[
                icon_item("🗂️", "Tonic Header",
                    "Logo, navigation with dropdowns, dual CTAs, and smart sticky scroll behavior. Collapses to a hamburger menu on mobile."),
                icon_item("🔗", "Tonic Footer",
                    "Logo, multi-column navigation, social links, and copyright bar. Switch to Minimal mode for landing pages."),
                icon_item("📢", "Announcement Bar",
                    "Site-wide banner above the header. Static or marquee scroll mode, icon, message text, and CTA button."),
            ],
            bg_type="light",
            columns="3",
        ),
        cta_banner(
            heading="Want the full module reference?",
            subheading="The documentation covers every field, every option, and every edge case for all 34 modules.",
            primary_label="Read the docs",
            primary_url="/docs/",
            bg_type="dark",
        ),
    ])


# ============================================================
# PAGE CONTENT: PRICING
# ============================================================

def pricing_page_content():
    return json.dumps([
        section_header(
            eyebrow="Pricing",
            heading="One price. One portal. Forever.",
            subheading="Buy Tonic once and use it forever. All future updates are included — no subscription, no renewal.",
            alignment="center",
            bg_type="light",
        ),
        cards_block(
            cards=[
                card("Single Portal",
                    "Full Tonic theme for one HubSpot portal. All 34 modules, 6 page templates, theme settings panel, blog module set, and all future updates.",
                    eyebrow="Most popular",
                    icon="🚀",
                    button_label="Buy on HubSpot Marketplace",
                    button_url="https://ecosystem.hubspot.com",
                    button_style="primary",
                ),
                card("Agency / Multi-Portal",
                    "Everything in Single Portal plus the right to install and use Tonic across unlimited client portals without additional per-portal fees.",
                    eyebrow="For agencies",
                    icon="🏢",
                    button_label="Contact us",
                    button_url="/contact/",
                    button_style="secondary",
                ),
                card("Custom Development",
                    "Need a custom module, a bespoke integration, or help getting Tonic deployed for a specific use case? Khaotic Digital builds on top of Tonic.",
                    eyebrow="Done for you",
                    icon="🛠️",
                    button_label="Get in touch",
                    button_url="/contact/",
                    button_style="secondary",
                ),
            ],
            columns="3",
            bg_type="alt",
        ),
        icon_feature_grid(
            eyebrow="What's included",
            heading="Everything. Upfront.",
            subtext="No add-ons, no feature tiers. One purchase gives you the complete theme.",
            items=[
                icon_item("✅", "All 34 modules", "Heroes, features, social proof, media, blog — the full library."),
                icon_item("✅", "6 page templates", "Home, landing, standard, blog listing, blog post, and system templates."),
                icon_item("✅", "Theme settings panel", "Brand colors, fonts, spacing, borders, buttons — all configurable without code."),
                icon_item("✅", "Blog module set", "8 global blog modules covering every blog template slot."),
                icon_item("✅", "Full documentation", "Installation guide, module reference, and customization docs."),
                icon_item("✅", "Lifetime updates", "Every update to Tonic goes to all existing customers at no extra cost."),
            ],
            bg_type="light",
        ),
        faq_block(
            eyebrow="FAQ",
            heading="Pricing questions",
            items=[
                faq_item("Is this a subscription?",
                    "No. Tonic is a one-time purchase. You own the theme forever and receive all future updates at no additional cost.", open_by_default=True),
                faq_item("Does the price include the HubSpot subscription?",
                    "No. Tonic is a theme that runs on HubSpot CMS. You need an active HubSpot CMS Hub subscription (Starter or above) separately."),
                faq_item("Can I use Tonic on client portals?",
                    "The single-portal license covers one HubSpot portal. If you're an agency installing Tonic across client accounts, the agency license is the right fit."),
                faq_item("What if a future HubSpot update breaks something?",
                    "We maintain Tonic for HubSpot CMS compatibility. When HubSpot makes breaking changes, we ship fixes as updates — included in your purchase."),
                faq_item("Do you offer refunds?",
                    "Refund policy is governed by the HubSpot Asset Marketplace terms. Contact us directly if you have an issue and we'll work to resolve it."),
            ],
            bg_type="light",
        ),
        cta_banner(
            heading="Ready to see it in action?",
            subheading="The site you're on right now is built entirely with Tonic modules and the default theme settings.",
            primary_label="Buy on HubSpot Marketplace",
            primary_url="https://ecosystem.hubspot.com",
            secondary_label="Read the docs first",
            secondary_url="/docs/",
            bg_type="primary",
        ),
    ])


# ============================================================
# PAGE CONTENT: CHANGELOG
# ============================================================

def changelog_page_content():
    return json.dumps([
        section_header(
            eyebrow="Changelog",
            heading="What's new in Tonic.",
            subheading="Every update, fix, and improvement — newest first.",
            alignment="left",
            bg_type="light",
        ),
        timeline_block(
            eyebrow="",
            heading="",
            items=[
                timeline_item("v1.1 — April 2026",
                    "Forms module + Timeline block",
                    "Added the Tonic Form module with HubSpot native form embed, custom label/placeholder overrides, inline and stacked layouts, and a thank-you message block. Added the Timeline module for date-labeled vertical sequences. Fixed a z-index conflict between the sticky header and Countdown Timer. Improved focus ring visibility across all interactive modules. 12 total bug fixes."),
                timeline_item("v1.0 — March 2026",
                    "Initial release",
                    "First public release of Tonic on the HubSpot Asset Marketplace. 32 modules, 6 page templates, CSS variable design token system, full blog module set, and theme settings panel."),
            ],
            bg_type="light",
        ),
        cta_banner(
            heading="Want to know when updates ship?",
            subheading="Follow Khaotic Digital on LinkedIn or check back here — we post every release.",
            primary_label="Follow on LinkedIn",
            primary_url="https://linkedin.com/company/khaoticdigital",
            bg_type="alt",
        ),
    ])


# ============================================================
# DOCS PAGE CONTENT
# ============================================================

# — Getting Started —

def doc_installation():
    return docs_body("""
<h2>Requirements</h2>
<p>Tonic runs on HubSpot CMS Hub. You need:</p>
<ul>
  <li>An active HubSpot CMS Hub account (Starter, Professional, or Enterprise)</li>
  <li>Access to Design Tools in your HubSpot portal</li>
</ul>

<h2>Step 1 — Purchase Tonic</h2>
<p>Buy Tonic from the HubSpot Asset Marketplace. Once purchased, the theme is immediately available in your HubSpot account.</p>

<h2>Step 2 — Apply the theme</h2>
<p>Go to <strong>Marketing → Files and Templates → Design Tools</strong>. In the left panel, find Tonic under Themes. Click <strong>Apply theme</strong> to set it as the default for your portal, or apply it to individual pages via the page editor.</p>

<h2>Step 3 — Configure theme settings</h2>
<p>With Tonic applied, go to <strong>Design Tools → Theme Settings</strong>. Set your brand colors, fonts, and spacing values. See <a href="/docs/getting-started/theme-settings/">Theme Settings</a> for the full reference.</p>

<h2>Step 4 — Build your first page</h2>
<p>Create a new website page, select Tonic as the template, and add modules using the drag-and-drop editor. Every Tonic module appears in the module library.</p>
""")


def doc_theme_settings():
    return docs_body("""
<h2>What are theme settings?</h2>
<p>Theme settings are the single source of truth for your site's design. Every Tonic module reads its colors, fonts, spacing, and border values from CSS custom properties that are driven by the theme settings panel.</p>
<p>Change a value in theme settings — every module on every page updates immediately. No custom CSS, no find-and-replace.</p>

<h2>Accessing theme settings</h2>
<p>Go to <strong>Marketing → Files and Templates → Design Tools</strong>, then click <strong>Theme Settings</strong> in the left panel while Tonic is the active theme.</p>

<h2>Available settings</h2>

<h3>Brand colors</h3>
<p><strong>Primary</strong> — Main brand color. Used for primary buttons, active states, links, and accents. Default: <code>#06B6D4</code>.</p>
<p><strong>Secondary</strong> — Supporting brand color. Used for secondary buttons and highlights. Default: <code>#10B981</code>.</p>
<p><strong>Accent</strong> — Tertiary color for decorative elements and callouts. Default: <code>#8B5CF6</code>.</p>

<h3>Typography</h3>
<p>Heading font, body font, and monospace font. Enter any Google Font name or a system font stack. Font size and weight for display, heading, body, and small text are individually configurable.</p>

<h3>Spacing &amp; layout</h3>
<p>Section padding (desktop and mobile), container max-width, container gutter, grid gutter, and row gap. These values drive spacing across all section-level modules.</p>

<h3>Borders &amp; shadows</h3>
<p>Default border radius, button radius, card radius, image radius, border color, border width, card shadow, and button shadow.</p>

<h3>Buttons</h3>
<p>Independent color controls for Primary, Secondary, Ghost, and Subtle button variants — background, hover, active, text color, and border. Plus text transform and font weight for all buttons.</p>
""")


def doc_page_templates():
    return docs_body("""
<h2>Available templates</h2>
<p>Tonic ships with six page templates. Each template determines which global modules are included and how the page structure is set up.</p>

<h3>Home template</h3>
<p>The main site homepage template. Includes the global header and footer. Full module library available in the drag-and-drop area. Use this for your site root page.</p>

<h3>Standard template</h3>
<p>General-purpose page template for About, Pricing, Contact, and any other marketing page. Global header and footer. Full module library available.</p>

<h3>Landing page template</h3>
<p>Conversion-focused template with the header navigation stripped down to logo-only. Ideal for ad campaign landing pages, event registrations, and lead capture pages. Footer uses the minimal variant.</p>

<h3>Blog listing template</h3>
<p>Pre-wired with the Blog Filter, Blog Listing, and Blog Pagination global modules in the standard HubSpot blog listing layout.</p>

<h3>Blog post template</h3>
<p>Pre-wired with the Blog Post Header, Blog Table of Contents, Blog Post Body, Blog Author Box, and Blog Related Posts global modules in the standard HubSpot blog post layout.</p>

<h3>System templates</h3>
<p>Error pages (404, 500, password-protected page, subscription confirmation). Tonic-styled and consistent with the rest of the site.</p>
""")


# — Module Reference —

def doc_heroes():
    return docs_body("""
<h2>Full Hero</h2>
<p>Full-width hero module. Content is centered or left-aligned over a background that can be a solid color (light, dark, primary, secondary, or custom), an image, or a video.</p>

<h3>Fields</h3>
<ul>
  <li><strong>Eyebrow</strong> — Small label above the heading. Use for category, announcement type, or page context.</li>
  <li><strong>Heading</strong> — Main H1. Keep under 10 words for impact.</li>
  <li><strong>Heading tag</strong> — H1 or H2. Always use H1 on the homepage hero.</li>
  <li><strong>Subheadline</strong> — Supporting text below the heading. One to two sentences max.</li>
  <li><strong>Primary CTA</strong> — Main conversion button. Label, URL, and style (uses theme button tokens).</li>
  <li><strong>Secondary CTA</strong> — Optional secondary action. Ghost style by default.</li>
  <li><strong>Background type</strong> — Light, Dark, Primary, Secondary, Image, or Video.</li>
  <li><strong>Background image</strong> — Shown when background type is Image. Uses HubSpot image picker.</li>
  <li><strong>Video URL</strong> — MP4 URL for background video. Falls back to background image on mobile.</li>
  <li><strong>Hero height</strong> — Small (400px), Medium (500px), Large (600px), or Full viewport.</li>
  <li><strong>Content alignment</strong> — Center or Left.</li>
</ul>

<h2>Split Hero</h2>
<p>Two-column hero with a text column and a media column. Media can be an image, MP4 video, or YouTube/Vimeo embed.</p>

<h3>Fields</h3>
<ul>
  <li><strong>Eyebrow, Heading, Heading tag, Subheadline, Primary CTA, Secondary CTA</strong> — Same as Full Hero.</li>
  <li><strong>Media type</strong> — Image, Video (MP4), or Embed (YouTube/Vimeo URL).</li>
  <li><strong>Media side</strong> — Right (default) or Left.</li>
  <li><strong>Split ratio</strong> — 50/50, 60/40, or 40/60.</li>
  <li><strong>Background type</strong> — Light, Dark, Primary, Secondary, or custom color.</li>
</ul>

<h2>Video Background Banner</h2>
<p>Autoplay background video with overlay content. Video is muted and loops by default. Falls back to a poster image on mobile and in browsers that block autoplay.</p>

<h2>CTA Banner</h2>
<p>Conversion-focused banner module. Two layouts: Centered (heading, subtext, and buttons stacked) and Split (heading/subtext on the left, buttons on the right).</p>

<h2>Split CTA</h2>
<p>Two-column CTA with a content column and a supporting column. Useful for pairing a conversion ask with a trust signal (testimonial snippet, logo grid, or stat).</p>

<h2>Announcement Bar</h2>
<p>Site-wide bar rendered above the global header. Controlled via the global module — edit once to update every page. Two scroll modes: Static (pinned) and Marquee (scrolling text). Includes an icon field, message text, and optional CTA button.</p>
""")


def doc_features():
    return docs_body("""
<h2>Icon Feature Grid</h2>
<p>The most-used module in Tonic. A grid of icon + heading + description items with configurable column count and item layout.</p>

<h3>Fields</h3>
<ul>
  <li><strong>Eyebrow, Heading, Subtext</strong> — Optional section header above the grid.</li>
  <li><strong>Items (repeater)</strong> — Each item has: Icon (emoji or SVG), Title, Description (rich text), optional Link text and URL.</li>
  <li><strong>Columns (desktop)</strong> — 2, 3, or 4. Always collapses to 1 column on mobile.</li>
  <li><strong>Item layout</strong> — Icon Top (icon above text) or Icon Left (icon inline with text).</li>
</ul>

<h2>Feature List</h2>
<p>Checklist-style feature display. Each item has an icon, title, description, and optional link. Good for "What's included" sections and comparison-adjacent content.</p>

<h2>Cards Repeater</h2>
<p>Flexible card grid. Each card supports a media area (image, icon, or none), eyebrow, heading, description, and button. Column count and media position are editor-controlled.</p>

<h3>Media position options</h3>
<ul>
  <li><strong>Top</strong> — Media above the card content. Standard blog-card style.</li>
  <li><strong>Left</strong> — Media to the left of text. Good for icon-driven feature lists in card form.</li>
  <li><strong>None</strong> — Text-only card with optional icon.</li>
</ul>

<h2>Process Steps</h2>
<p>Numbered or icon-driven step sequence. Optional connector lines between steps. Two orientations: Horizontal (left to right) and Vertical (stacked).</p>

<h3>Fields per step</h3>
<ul>
  <li><strong>Node type</strong> — Number (auto-incremented) or Icon (custom emoji/SVG).</li>
  <li><strong>Step title</strong> — Heading for this step.</li>
  <li><strong>Description</strong> — Rich text body for this step.</li>
  <li><strong>Link text / URL</strong> — Optional "Learn more" link per step.</li>
</ul>

<h2>Timeline</h2>
<p>Date-labeled vertical timeline. Each item has a date label, heading, and description. Useful for company history, product roadmaps, case study progression, and event sequences.</p>

<h2>Section Header</h2>
<p>Standalone eyebrow + heading + subheading + optional CTA module. Use between content sections when you need a titled separator without a full content block. Supports left, center, and right text alignment.</p>
""")


def doc_social_proof():
    return docs_body("""
<h2>Testimonials Grid</h2>
<p>Star-rated testimonial cards in a configurable grid. Each card includes star rating, quote, author name, author title, company name, avatar image, and company logo.</p>

<h3>Fields</h3>
<ul>
  <li><strong>Eyebrow, Heading, Subheading</strong> — Optional section header above the grid.</li>
  <li><strong>Testimonials (repeater)</strong> — Each item: star rating (1–5), quote, author name, author title, company name, avatar (image picker), company logo (image picker).</li>
  <li><strong>Columns (desktop)</strong> — 2 or 3.</li>
</ul>

<h2>Testimonials Slider</h2>
<p>Auto-advancing carousel of testimonial cards. Same per-item fields as Testimonials Grid. Manual navigation via prev/next arrows and dot indicators. Autoplay speed is configurable in the Style tab.</p>

<h2>Stats and Numbers</h2>
<p>Animated countup stat display. Each stat has a prefix (e.g. "$"), number, suffix (e.g. "M+"), label, and optional description. Two display styles: Inline (divider-separated) and Card (each stat in a bordered card).</p>

<h3>Countup animation</h3>
<p>Enabled by default. Triggers when the module enters the viewport. Can be disabled per-module in the Style tab.</p>

<h2>Logos Scroller</h2>
<p>Client and partner logo display. Two modes: Grid (static, configurable columns) and Marquee (auto-scrolling, left or right direction). Each logo has an image field and an optional link URL. A text label is shown as fallback when no image is uploaded.</p>

<h2>Team Grid</h2>
<p>Team member cards in a configurable column grid. Each member: photo, name, job title, bio, and social links (LinkedIn, Twitter, Instagram, personal website). Photo shape options: Square, Circle.</p>
""")


def doc_blog_modules():
    return docs_body("""
<h2>Overview</h2>
<p>Tonic's blog system consists of eight global modules designed to slot into HubSpot's standard blog template areas. They are pre-wired in the Tonic blog listing and blog post templates — you don't need to configure them unless you want to customize defaults.</p>

<h2>Blog Listing</h2>
<p>The main post grid for the blog index page. Automatically adapts its layout for four contexts:</p>
<ul>
  <li><strong>Default listing</strong> — All posts, newest first, paginated.</li>
  <li><strong>Tag filter</strong> — Posts filtered by the active topic tag.</li>
  <li><strong>Author filter</strong> — Posts filtered by author.</li>
  <li><strong>Simple list (/all)</strong> — Compact list view of all posts.</li>
</ul>

<h2>Blog Filter</h2>
<p>Topic/tag pill bar. Reads all HubSpot blog topics and generates the correct filter URLs. The active topic pill reflects the current filter. Place above the Blog Listing module in the listing template.</p>

<h2>Blog Pagination</h2>
<p>Wired to HubSpot's native pagination variables. Only renders when there is more than one page. Three styles selectable in the module settings: <strong>Numbered</strong>, <strong>Simple</strong> (previous/next only), and <strong>Minimal</strong> (older/newer text links).</p>

<h2>Blog Post Header</h2>
<p>Global module that renders at the top of every blog post. Displays: featured image, category tag, post title, author name and avatar, publish date, estimated read time, and topic tags.</p>

<h2>Blog Table of Contents</h2>
<p>Automatically scans the post body for H2 and H3 headings and generates a linked table of contents. Smooth-scroll jump links. Active section tracking as the reader scrolls. Collapses to a toggle dropdown on mobile. Configurable heading depth (H2 only or H2 + H3).</p>

<h2>Blog Post Body</h2>
<p>Global wrapper module for the HubSpot post content editor output. Applies Tonic's <code>.prose</code> typography styles — optimized line height, heading scale, link styling, blockquote styling, and code block formatting — to the post body.</p>

<h2>Blog Author Box</h2>
<p>Displays below the post body when the post has an assigned author. Shows: avatar, name, bio, and social links. Reads from the HubSpot author record.</p>

<h2>Blog Related Posts</h2>
<p>Shows at the end of each post. Scores related posts by content similarity and shared topic tags. Displays as a card grid with featured image, topic tag, title, author, date, and excerpt. Card count (3 or 4) is configurable.</p>
""")


# ============================================================
# COMMAND
# ============================================================

class Command(BaseCommand):
    help = "Create the Tonic theme catalog and documentation site."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing catalog pages before creating new ones.",
        )

    def handle(self, *args, **options):
        from tonictail.cms.models import (
            HomePage, GeneralPage,
            BlogIndexPage, DocsIndexPage, DocsSectionPage, DocsPage,
        )

        self.stdout.write(self.style.MIGRATE_HEADING("Tonic catalog loader"))

        root = Page.objects.filter(depth=1).first()
        if not root:
            self.stdout.write(self.style.ERROR("No root page found. Run migrations first."))
            return

        # ── Optional reset ────────────────────────────────────────────────
        if options["reset"]:
            self.stdout.write("  Removing existing catalog pages...")
            for slug in ["home", "modules", "pricing", "changelog", "docs"]:
                HomePage.objects.filter(slug=slug).delete()
                GeneralPage.objects.filter(slug=slug).delete()
                DocsIndexPage.objects.filter(slug=slug).delete()
                BlogIndexPage.objects.filter(slug="blog").delete()

        # ── Home ──────────────────────────────────────────────────────────
        # ── Home ──────────────────────────────────────────────────────────
        home = HomePage.objects.filter(slug="home").first()
        if not home:
            existing = root.get_children().filter(slug="home").first()
            if existing:
                existing.delete()
                root.refresh_from_db()  # ← add this

            home = HomePage(
                title="Tonic — A HubSpot CMS Theme by Khaotic Digital",
                slug="home",
                body=json.loads(home_page_content()),
            )
            root.add_child(instance=home)
            home.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Home page"))

        # ── Point site at home ────────────────────────────────────────────
        site = Site.objects.first()
        if site and site.root_page_id != home.id:
            site.root_page = home
            site.site_name = "Tonic by Khaotic Digital"
            site.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Site root updated"))

        # ── Modules catalog ───────────────────────────────────────────────
        if not GeneralPage.objects.filter(slug="modules").exists():
            modules_page = GeneralPage(
                title="Modules",
                slug="modules",
                intro="All 34 Tonic modules — reference and documentation.",
                body=json.loads(modules_page_content()),
            )
            home.add_child(instance=modules_page)
            modules_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Modules catalog page"))

        # ── Pricing ───────────────────────────────────────────────────────
        if not GeneralPage.objects.filter(slug="pricing").exists():
            pricing = GeneralPage(
                title="Pricing",
                slug="pricing",
                intro="Buy Tonic once. Use it forever.",
                body=json.loads(pricing_page_content()),
            )
            home.add_child(instance=pricing)
            pricing.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Pricing page"))

        # ── Changelog ─────────────────────────────────────────────────────
        if not GeneralPage.objects.filter(slug="changelog").exists():
            changelog = GeneralPage(
                title="Changelog",
                slug="changelog",
                intro="Every Tonic update, fix, and improvement.",
                body=json.loads(changelog_page_content()),
            )
            home.add_child(instance=changelog)
            changelog.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Changelog page"))

        # ── Docs ──────────────────────────────────────────────────────────
        docs = DocsIndexPage.objects.filter(slug="docs").first()
        if not docs:
            docs = DocsIndexPage(
                title="Documentation",
                slug="docs",
                intro="<p>Everything you need to install, configure, and get the most out of Tonic.</p>",
            )
            home.add_child(instance=docs)
            docs.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Docs index"))

            # — Getting Started section —
            getting_started = DocsSectionPage(
                title="Getting Started",
                slug="getting-started",
                intro="Install Tonic and configure it for your portal.",
            )
            docs.add_child(instance=getting_started)
            getting_started.save_revision().publish()

            for title, slug, body_fn in [
                ("Installation",    "installation",    doc_installation),
                ("Theme Settings",  "theme-settings",  doc_theme_settings),
                ("Page Templates",  "page-templates",  doc_page_templates),
            ]:
                dp = DocsPage(title=title, slug=slug, body=body_fn())
                getting_started.add_child(instance=dp)
                dp.save_revision().publish()

            self.stdout.write(self.style.SUCCESS("  ✓ Getting Started (3 pages)"))

            # — Module Reference section —
            module_ref = DocsSectionPage(
                title="Module Reference",
                slug="modules",
                intro="Field-by-field reference for every Tonic module.",
            )
            docs.add_child(instance=module_ref)
            module_ref.save_revision().publish()

            for title, slug, body_fn in [
                ("Heroes & Banners",        "heroes",        doc_heroes),
                ("Features & Content",      "features",      doc_features),
                ("Social Proof",            "social-proof",  doc_social_proof),
                ("Blog Modules",            "blog",          doc_blog_modules),
            ]:
                dp = DocsPage(title=title, slug=slug, body=body_fn())
                module_ref.add_child(instance=dp)
                dp.save_revision().publish()

            self.stdout.write(self.style.SUCCESS("  ✓ Module Reference (4 pages)"))

        # ── Summary ───────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Tonic catalog loaded."))
        self.stdout.write("")
        self.stdout.write("Pages created:")
        self.stdout.write("  /            → Home (full marketing page)")
        self.stdout.write("  /modules/    → Module catalog")
        self.stdout.write("  /pricing/    → Pricing")
        self.stdout.write("  /changelog/  → Changelog / release notes")
        self.stdout.write("  /docs/       → Docs index")
        self.stdout.write("               └── Getting Started")
        self.stdout.write("                   ├── Installation")
        self.stdout.write("                   ├── Theme Settings")
        self.stdout.write("                   └── Page Templates")
        self.stdout.write("               └── Module Reference")
        self.stdout.write("                   ├── Heroes & Banners")
        self.stdout.write("                   ├── Features & Content")
        self.stdout.write("                   ├── Social Proof")
        self.stdout.write("                   └── Blog Modules")