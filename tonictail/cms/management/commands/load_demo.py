"""
Management command: load_demo
Usage: python manage.py load_demo

Creates a fully populated demo site with placeholder pages and content
so buyers see a working site immediately after setup. Safe to re-run —
checks for existing pages before creating.

Author: Jonathan Sumner | jonathan@khaoticdigital.com
Theme: Tonictail — Khaotic Digital, LLC
"""

import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wagtail.models import Page, Site
from wagtail.rich_text import RichText

User = get_user_model()


# ============================================================
# BLOCK CONTENT HELPERS
# ============================================================
# StreamField content is stored as JSON. These helpers produce
# the correct Wagtail StreamField JSON format for each block type.

def block(block_type, value):
    """Wrap a value in Wagtail StreamField block format."""
    import uuid
    return {"type": block_type, "value": value, "id": str(uuid.uuid4())}


def btn(label, url="/", style="primary", size="md"):
    return {"label": label, "url": url, "style": style, "size": size, "open_in_new_tab": False}


def background(bg_type="light"):
    return {"background_type": bg_type}


def rich(html):
    """Wagtail stores richtext as a string with <p> tags."""
    return html


# ============================================================
# BLOCK DEFINITIONS
# ============================================================

def hero_full(heading, subheadline, eyebrow="", primary_label="Get started", primary_url="/",
              secondary_label="Learn more", secondary_url="#", bg_type="dark"):
    return block("full_hero", {
        "eyebrow": eyebrow,
        "heading": heading,
        "heading_tag": "h1",
        "subheadline": subheadline,
        "primary_cta": btn(primary_label, primary_url, "primary", "lg"),
        "secondary_cta": btn(secondary_label, secondary_url, "ghost", "lg"),
        "background_type": bg_type,
        "background_image": None,
        "video_url": "",
        "hero_height": "large",
        "content_alignment": "center",
    })


def section_header(heading, subheading="", eyebrow="", alignment="center",
                   primary_label="", primary_url="", bg_type="light", show_divider=False):
    return block("section_header", {
        "eyebrow": eyebrow,
        "heading": heading,
        "heading_level": "h2",
        "subheading": subheading,
        "primary_cta": btn(primary_label, primary_url) if primary_label else btn("", ""),
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


def stats_row(eyebrow, heading, stats, bg_type="light", columns="3", dividers=True):
    return block("stats", {
        "eyebrow": eyebrow,
        "heading": heading,
        "subheading": "",
        "stats": stats,
        "columns_desktop": columns,
        "show_dividers": dividers,
        "show_card_style": False,
        "enable_countup": True,
        "background": background(bg_type),
    })


def stat(number, label, prefix="", suffix="", description=""):
    return {"prefix": prefix, "number": number, "suffix": suffix,
            "stat_label": label, "description": description}


def cta_banner(heading, subheading, primary_label, primary_url, secondary_label="",
               secondary_url="", bg_type="primary", eyebrow=""):
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


def richtext_block(html, container="container-md", bg_type="light"):
    return block("rich_text", {
        "rich_text": rich(html),
        "container_width": container,
        "text_alignment": "left",
        "background": background(bg_type),
    })


def cards_block(cards, columns="3", bg_type="light", media_position="top"):
    return block("cards", {
        "cards": cards,
        "columns_desktop": columns,
        "media_position": media_position,
        "background": background(bg_type),
    })


def card(title, description, eyebrow="", button_label="", button_url="",
         button_style="subtle", icon="", media_type="icon"):
    return {
        "media_type": media_type,
        "image": None,
        "icon": icon,
        "eyebrow": eyebrow,
        "title": title,
        "description": rich(f"<p>{description}</p>"),
        "button_label": button_label,
        "button_url": button_url,
        "button_style": button_style,
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


def logo_grid(eyebrow, logos, bg_type="alt", columns="5", display_mode="grid"):
    return block("logo_grid", {
        "eyebrow": eyebrow,
        "logos": logos,
        "display_mode": display_mode,
        "columns_desktop": columns,
        "scroll_direction": "left",
        "background": background(bg_type),
    })


def logo(company_name, link_url=""):
    return {"logo_image": None, "company_name": company_name, "link_url": link_url}


def split_hero(heading, subheadline, eyebrow="", primary_label="", primary_url="",
               secondary_label="", secondary_url="", media_side="right", bg_type="light"):
    return block("split_hero", {
        "eyebrow": eyebrow,
        "heading": heading,
        "heading_tag": "h1",
        "subheadline": subheadline,
        "primary_cta": btn(primary_label, primary_url) if primary_label else btn("", ""),
        "secondary_cta": btn(secondary_label, secondary_url, "secondary") if secondary_label else btn("", ""),
        "media_type": "image",
        "image": None,
        "video_url": "",
        "embed_url": "",
        "media_side": media_side,
        "split_ratio": "50-50",
        "background_type": bg_type,
    })


def team_grid(eyebrow, heading, members, bg_type="light", columns="4"):
    return block("team_grid", {
        "eyebrow": eyebrow,
        "heading": heading,
        "subtext": rich(""),
        "members": members,
        "columns_desktop": columns,
        "photo_shape": "square",
        "text_alignment": "center",
        "background": background(bg_type),
    })


def team_member(name, title, bio=""):
    return {
        "photo": None,
        "name": name,
        "job_title": title,
        "bio": rich(f"<p>{bio}</p>") if bio else rich(""),
        "linkedin": "",
        "twitter": "",
        "instagram": "",
        "website": "",
    }


def feature_list(eyebrow, heading, items, bg_type="light", columns="3", layout="icon-top"):
    return block("feature_list", {
        "eyebrow": eyebrow,
        "heading": heading,
        "subheading": rich(""),
        "items": items,
        "item_layout": layout,
        "columns_desktop": columns,
        "background": background(bg_type),
    })


def feature_item(icon, title, description, link_text="", link_url=""):
    return {
        "icon": icon,
        "title": title,
        "description": rich(f"<p>{description}</p>"),
        "link_text": link_text,
        "link_url": link_url,
    }


def announcement_bar(message, cta_label="", cta_url="", scroll_mode="static"):
    return block("announcement_bar", {
        "message_text": message,
        "show_cta": bool(cta_label),
        "cta_label": cta_label,
        "cta_url": cta_url,
        "scroll_mode": scroll_mode,
    })


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


# ============================================================
# PAGE CONTENT DEFINITIONS
# ============================================================

def home_page_content():
    return json.dumps([
        announcement_bar(
            "🚀 Tonictail is now available — the Django + Wagtail SaaS boilerplate.",
            cta_label="Learn more",
            cta_url="/about/",
        ),
        hero_full(
            heading="The Django SaaS boilerplate that ships with everything.",
            subheadline="Wagtail CMS, Stripe billing, HubSpot sync, UTM tracking, and a full marketing component library — all wired up so you can focus on your product.",
            eyebrow="Built for developers who build for marketers",
            primary_label="Get started free",
            primary_url="/accounts/signup/",
            secondary_label="View docs",
            secondary_url="/docs/",
            bg_type="dark",
        ),
        logo_grid(
            eyebrow="Trusted by teams using these tools",
            logos=[
                logo("HubSpot"), logo("Stripe"), logo("Celery"),
                logo("Wagtail"), logo("Django"), logo("Postgres"),
            ],
            bg_type="alt",
        ),
        icon_feature_grid(
            eyebrow="Why Tonictail",
            heading="Everything a marketing-ready SaaS needs.",
            subtext="Stop rebuilding the same infrastructure. Tonictail ships with the plumbing so you ship the product.",
            items=[
                icon_item("🎨", "Tonic CSS Framework", "A full design token system driven by Wagtail Theme Settings. Change a color — every component updates."),
                icon_item("📦", "44 Content Blocks", "Every block from the Tonic HubSpot theme ported to Wagtail StreamField. Heroes, FAQs, sliders, galleries, and more."),
                icon_item("💳", "Stripe Ready", "dj-stripe configured for subscriptions and one-time payments. Customer portal, webhook handling, and access gating included."),
                icon_item("🔗", "HubSpot CRM Sync", "Contact create and update on signup and form submission. UTM tracking wired to the campaign model from day one."),
                icon_item("📧", "Transactional Email", "django-anymail with Postmark or Resend. Welcome emails, receipts, and password reset all templated and ready."),
                icon_item("🚀", "One-Command Deploy", "Docker + Render, Railway, or Fly.io configs included. Clone, configure, deploy."),
            ],
            bg_type="light",
        ),
        stats_row(
            eyebrow="By the numbers",
            heading="Weeks of setup, shipped in a day.",
            stats=[
                stat("44", "Content blocks", suffix="+"),
                stat("10", "Minutes to first running site"),
                stat("100", "Theme token variables", suffix="%"),
                stat("0", "Hardcoded colors in components"),
            ],
            bg_type="alt",
            columns="4",
        ),
        process_steps(
            eyebrow="How it works",
            heading="From clone to live in three steps.",
            steps=[
                step("Clone and configure", "Run the setup command, enter your Stripe keys and domain, and configure your brand colors in Wagtail admin."),
                step("Build your product", "Add your app logic. The boilerplate handles auth, billing, email, and CMS — you handle the unique parts."),
                step("Deploy and sell", "Push to your host of choice. The demo site, docs, and marketing pages are already live."),
            ],
            bg_type="light",
        ),
        testimonials_grid(
            eyebrow="What developers say",
            heading="Built by a developer who builds for marketers.",
            testimonials=[
                testimonial(
                    "Finally a Django boilerplate that understands marketing ops. The HubSpot sync alone saved me two weeks.",
                    "Alex R.", "Freelance Developer",
                ),
                testimonial(
                    "The Tonic CSS framework is legitimately great. I changed my primary color in Wagtail settings and every component updated instantly.",
                    "Maria S.", "Agency Developer",
                ),
                testimonial(
                    "I've tried every Next.js boilerplate. This is the first Django one that takes marketing infrastructure as seriously as app architecture.",
                    "James T.", "Indie Hacker",
                ),
            ],
            bg_type="alt",
        ),
        cta_banner(
            heading="Ready to stop rebuilding the plumbing?",
            subheading="Get the full Tonictail boilerplate and ship your SaaS on a foundation built for marketing from day one.",
            primary_label="Get Tonictail",
            primary_url="/pricing/",
            secondary_label="Read the docs",
            secondary_url="/docs/",
            bg_type="primary",
        ),
    ])


def about_page_content():
    return json.dumps([
        split_hero(
            eyebrow="About Tonictail",
            heading="Built by a developer who's spent 20 years in marketing infrastructure.",
            subheadline="Tonictail exists because every agency project starts the same way — rebuilding auth, billing, CMS, and email before writing a single line of actual product code.",
            primary_label="Read the docs",
            primary_url="/docs/",
            secondary_label="Get started",
            secondary_url="/accounts/signup/",
            media_side="right",
            bg_type="light",
        ),
        richtext_block(
            html="""<h2>The problem</h2>
<p>Every SaaS project needs the same foundation: authentication, payments, transactional email, a content management system, and marketing infrastructure. Developers spend weeks — sometimes months — building this before they can write a single line of product code.</p>
<p>Marc Louvion solved this for Next.js developers with ShipFast. But the Django and Wagtail ecosystem — despite being more mature, more production-proven, and frankly better suited to content-heavy marketing sites — had nothing comparable.</p>
<h2>The solution</h2>
<p>Tonictail is the Django + Wagtail equivalent. It ships with Cookiecutter Django as the base, Wagtail as the CMS layer, dj-stripe for payments, django-anymail for transactional email, and the full Tonic component library — 44 marketing blocks ported from a production HubSpot theme.</p>
<p>But where ShipFast stops at the CMS layer, Tonictail goes further. It includes UTM tracking wired to a Campaign model, HubSpot CRM sync as a first-class feature, and marketing infrastructure baked into the architecture — not bolted on as an afterthought.</p>""",
            container="container-md",
        ),
        team_grid(
            eyebrow="The team",
            heading="Built by Khaotic Digital",
            members=[
                team_member(
                    "Jonathan Sumner",
                    "Founder, Khaotic Digital LLC",
                    "20 years building marketing and sales infrastructure for agencies and brands. HubSpot CMS developer, Django engineer, and the person who got tired of rebuilding the same boilerplate.",
                ),
            ],
            columns="3",
        ),
        cta_banner(
            heading="Want to contribute?",
            subheading="Tonictail is open to contributions. If you've built something that belongs in the boilerplate, open a PR.",
            primary_label="View on GitHub",
            primary_url="https://github.com",
            bg_type="dark",
        ),
    ])


def pricing_page_content():
    return json.dumps([
        section_header(
            eyebrow="Simple pricing",
            heading="One price. Everything included.",
            subheading="No subscriptions. No tiers. Buy once, use forever, get all future updates.",
            alignment="center",
            bg_type="light",
        ),
        cards_block(
            cards=[
                card(
                    title="Tonictail",
                    description="The complete Django + Wagtail SaaS boilerplate. Full source code, all 44 blocks, Stripe integration, HubSpot sync, docs, and lifetime updates.",
                    eyebrow="One-time purchase",
                    button_label="Buy now — $149",
                    button_url="/checkout/",
                    button_style="primary",
                    icon="🚀",
                ),
                card(
                    title="Agency license",
                    description="Everything in Tonictail plus the right to use it across unlimited client projects without attribution. Includes priority support.",
                    eyebrow="Agency license",
                    button_label="Buy now — $349",
                    button_url="/checkout/?plan=agency",
                    button_style="primary",
                    icon="🏢",
                ),
                card(
                    title="Consulting",
                    description="Need help with setup, customisation, or a custom integration? Book a session with the Khaotic Digital team.",
                    eyebrow="Custom work",
                    button_label="Get in touch",
                    button_url="/contact/",
                    button_style="secondary",
                    icon="💬",
                ),
            ],
            columns="3",
            bg_type="alt",
        ),
        faq_block(
            eyebrow="FAQ",
            heading="Common questions",
            items=[
                faq_item("Is this a subscription?", "No. You pay once and own the code forever. Future updates to the boilerplate are included at no extra cost.", open_by_default=True),
                faq_item("Can I use it for client projects?", "The standard license covers one project (including commercial use). The agency license covers unlimited client projects."),
                faq_item("What stack does it use?", "Django 5.2, Wagtail 6, Cookiecutter Django, dj-stripe, django-anymail, Celery, Postgres, Docker, and the Tonic CSS framework."),
                faq_item("Is there a demo?", "Yes — the site you're on right now runs on Tonictail. Everything you see is built with the included blocks and theme."),
                faq_item("Do I need to know Wagtail?", "Basic Django knowledge is enough to get started. The documentation covers the Wagtail-specific parts. The boilerplate is designed to be approachable."),
                faq_item("What if I need help?", "Documentation is included. For custom work or support, the consulting option gets you direct access to the team."),
            ],
            bg_type="light",
        ),
        cta_banner(
            heading="Still have questions?",
            subheading="Reach out directly. We're happy to help you figure out if Tonictail is the right fit.",
            primary_label="Get in touch",
            primary_url="/contact/",
            bg_type="dark",
        ),
    ])


def contact_page_content():
    return json.dumps([
        section_header(
            eyebrow="Get in touch",
            heading="We'd love to hear from you.",
            subheading="Questions about Tonictail, custom work, or just want to say hi — use the form or reach out directly.",
            alignment="center",
            bg_type="light",
        ),
        block("contact_info", {
            "eyebrow": "",
            "heading": "Contact details",
            "subheading": "",
            "show_address": False,
            "street": "",
            "city_state_zip": "",
            "country": "",
            "directions_text": "",
            "directions_url": "",
            "show_phone": False,
            "primary_number": "",
            "secondary_number": "",
            "show_email": True,
            "primary_email": "hello@khaoticdigital.com",
            "secondary_email": "",
            "show_hours": True,
            "hours_text": rich("<p>Monday – Friday, 9am – 5pm CT</p>"),
            "columns": "2",
            "background": background("alt"),
        }),
    ])


def blog_index_intro():
    return "<p>Thoughts on Django, Wagtail, marketing infrastructure, and building software products for the long term.</p>"


def docs_intro():
    return "<p>Everything you need to set up, configure, and customise Tonictail.</p>"


# ============================================================
# COMMAND
# ============================================================

class Command(BaseCommand):
    help = "Create demo pages with placeholder content for the Tonictail theme."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo pages before creating new ones.",
        )

    def handle(self, *args, **options):
        from tonictail.cms.models import (
            HomePage, GeneralPage, LandingPage,
            BlogIndexPage, DocsIndexPage, DocsSectionPage, DocsPage,
        )

        self.stdout.write(self.style.MIGRATE_HEADING("Tonictail demo loader"))

        # ── Find or create root ──────────────────────────────────────────────
        root = Page.objects.filter(depth=1).first()
        if not root:
            self.stdout.write(self.style.ERROR("No root page found. Run migrations first."))
            return

        # ── Reset if requested ───────────────────────────────────────────────
        if options["reset"]:
            self.stdout.write("  Removing existing demo pages...")
            for slug in ["home", "about", "pricing", "contact", "blog", "docs"]:
                HomePage.objects.filter(slug=slug).delete()
                GeneralPage.objects.filter(slug=slug).delete()
                BlogIndexPage.objects.filter(slug=slug).delete()
                DocsIndexPage.objects.filter(slug=slug).delete()

        # ── Home page ────────────────────────────────────────────────────────
        home = HomePage.objects.filter(slug="home").first()
        if not home:
            home = HomePage(
                title="Home",
                slug="home",
                body=json.loads(home_page_content()),
            )
            root.add_child(instance=home)
            home.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Home page created"))
        else:
            self.stdout.write("  — Home page already exists, skipping")

        # ── Point the default site at home ───────────────────────────────────
        site = Site.objects.first()
        if site and site.root_page_id != home.id:
            site.root_page = home
            site.hostname = "localhost"
            site.port = 8000
            site.site_name = "Tonictail"
            site.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Site root updated to Home page"))

        # ── About ────────────────────────────────────────────────────────────
        if not GeneralPage.objects.filter(slug="about").exists():
            about = GeneralPage(
                title="About",
                slug="about",
                intro="The story behind Tonictail and the team at Khaotic Digital.",
                body=json.loads(about_page_content()),
            )
            home.add_child(instance=about)
            about.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ About page created"))

        # ── Pricing ──────────────────────────────────────────────────────────
        if not GeneralPage.objects.filter(slug="pricing").exists():
            pricing = GeneralPage(
                title="Pricing",
                slug="pricing",
                intro="Simple, one-time pricing for the Tonictail boilerplate.",
                body=json.loads(pricing_page_content()),
            )
            home.add_child(instance=pricing)
            pricing.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Pricing page created"))

        # ── Contact ──────────────────────────────────────────────────────────
        if not GeneralPage.objects.filter(slug="contact").exists():
            contact = GeneralPage(
                title="Contact",
                slug="contact",
                intro="Get in touch with the Khaotic Digital team.",
                body=json.loads(contact_page_content()),
            )
            home.add_child(instance=contact)
            contact.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Contact page created"))

        # ── Blog ─────────────────────────────────────────────────────────────
        blog = BlogIndexPage.objects.filter(slug="blog").first()
        if not blog:
            blog = BlogIndexPage(
                title="Blog",
                slug="blog",
                intro=blog_index_intro(),
            )
            home.add_child(instance=blog)
            blog.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Blog index created"))

            # Sample blog posts
            from tonictail.cms.models import BlogPostPage
            posts = [
                ("Getting started with Tonictail",
                 "getting-started-with-tonictail",
                 "A walkthrough of the setup process from clone to a running site in under 10 minutes.",
                 json.dumps([richtext_block("""<h2>Prerequisites</h2>
<p>You'll need Docker, Python 3.12, and uv installed. Everything else is handled by the project setup.</p>
<h2>Clone and configure</h2>
<p>Clone the repo, copy the <code>.env.example</code> to <code>.env</code>, and fill in your Stripe keys, database URL, and email credentials.</p>
<h2>Run migrations and load the demo</h2>
<p>Run <code>just manage migrate</code> and then <code>just manage load_demo</code> to populate the site with placeholder content. You'll see a fully built marketing site immediately.</p>""")])),
                ("Why Django is underrated for SaaS",
                 "why-django-is-underrated-for-saas",
                 "The Django ecosystem is mature, stable, and has everything you need to build and ship a SaaS product.",
                 json.dumps([richtext_block("""<h2>The perception problem</h2>
<p>The indie hacker community has largely moved to Next.js and TypeScript. Django is seen as the old guard — enterprise, slow-moving, not exciting. That perception is wrong.</p>
<h2>What Django actually gives you</h2>
<p>Django ships with a battle-tested ORM, a built-in admin, a forms library, authentication, and a security model that's been hardened over 15 years. Wagtail adds a production-grade CMS on top.</p>
<p>The ecosystem — dj-stripe, django-allauth, django-anymail, Celery — covers everything a SaaS needs. And unlike JavaScript fatigue, the Django way of doing things doesn't change every six months.</p>""")])),
                ("Building marketing infrastructure that lasts",
                 "building-marketing-infrastructure-that-lasts",
                 "UTM tracking, CRM sync, and lead capture done right at the architecture level.",
                 json.dumps([richtext_block("""<h2>The problem with most developer tools</h2>
<p>Most developer-focused SaaS boilerplates treat marketing as an afterthought. They wire up Stripe and call it done. But a SaaS product's ability to grow depends entirely on the quality of its marketing infrastructure.</p>
<h2>What marketing infrastructure actually means</h2>
<p>It means capturing UTM parameters at the session layer and persisting them to the user record at signup. It means syncing contacts to your CRM on the right triggers. It means knowing which campaign drove which conversion.</p>
<p>Tonictail builds this in from the start because it was designed by someone who has spent 20 years building exactly this for marketing teams.</p>""")])),
            ]
            for title, slug, intro, body in posts:
                post = BlogPostPage(
                    title=title, slug=slug, intro=intro,
                    body=json.loads(body),
                )
                blog.add_child(instance=post)
                post.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"  ✓ {len(posts)} blog posts created"))

        # ── Docs ─────────────────────────────────────────────────────────────
        docs = DocsIndexPage.objects.filter(slug="docs").first()
        if not docs:
            docs = DocsIndexPage(
                title="Documentation",
                slug="docs",
                intro=docs_intro(),
            )
            home.add_child(instance=docs)
            docs.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  ✓ Docs index created"))

            from wagtail.blocks import RichTextBlock as RTB

            # Getting started section
            getting_started = DocsSectionPage(
                title="Getting Started",
                slug="getting-started",
                intro="Everything you need to get Tonictail running locally and deployed.",
            )
            docs.add_child(instance=getting_started)
            getting_started.save_revision().publish()

            doc_pages = [
                ("Installation", "installation",
                 [{"type": "rich_text", "id": "1", "value": "<h2>Requirements</h2><p>Python 3.12, Docker, uv, and a Postgres database. See the README for full prerequisites.</p><h2>Clone the repo</h2><pre><code>git clone https://github.com/yourname/tonictail.git\ncd tonictail\ncp .env.example .env</code></pre><h2>Configure your environment</h2><p>Edit <code>.env</code> and set your <code>DATABASE_URL</code>, <code>STRIPE_LIVE_SECRET_KEY</code>, and email credentials.</p><h2>Run setup</h2><pre><code>uv sync\njust manage migrate\njust manage createsuperuser\njust manage load_demo\njust up</code></pre><p>Visit <code>http://localhost:8000</code> — you should see the fully populated demo site.</p>"}]),
                ("Theme settings", "theme-settings",
                 [{"type": "rich_text", "id": "2", "value": "<h2>How theme settings work</h2><p>Tonictail uses a Wagtail <code>SiteSetting</code> model called <code>ThemeSettings</code> to store design tokens. These are rendered into a CSS file at <code>/theme/theme-vars.css</code> as CSS custom properties.</p><p>Go to Wagtail admin → Settings → Theme settings to change colors, fonts, spacing, and border radii. Every component in the Tonic CSS framework reads from these tokens — change a value and every component updates on next page load.</p><h2>Available tokens</h2><p>Brand colors, text colors, backgrounds, borders, shadows, button variants, form inputs, section spacing, and typography — all configurable without touching code.</p>"}]),
                ("Content blocks", "content-blocks",
                 [{"type": "rich_text", "id": "3", "value": "<h2>The block library</h2><p>Tonictail ships with 44 content blocks ported from the Tonic HubSpot theme. Every block is available on the General page, Home page, Landing page, and Blog post page types.</p><p>Blocks are added and configured in the Wagtail admin page editor using the StreamField interface. Click the + button to add a block, choose the type, and fill in the fields.</p><h2>Block categories</h2><ul><li><strong>Heroes</strong> — Full hero, split hero, video banner</li><li><strong>Content</strong> — Rich text, image + text, image figure, embed, video, code</li><li><strong>Marketing</strong> — CTA banner, split CTA, announcement bar, button group</li><li><strong>Features</strong> — Feature list, icon feature grid, cards</li><li><strong>Social proof</strong> — Testimonials grid, testimonials slider, logo grid, stats</li><li><strong>Navigation</strong> — FAQ accordion, tabs and panels, breadcrumbs</li><li><strong>Media</strong> — Image gallery, slider</li><li><strong>Team / contact</strong> — Team grid, contact info, map embed, countdown timer</li><li><strong>Process</strong> — Process steps, timeline</li><li><strong>Data</strong> — Comparison table</li></ul>"}]),
                ("Deployment", "deployment",
                 [{"type": "rich_text", "id": "4", "value": "<h2>Deploy to Render</h2><p>Tonictail ships with a <code>render.yaml</code> file. Connect your GitHub repo to Render, select the config file, and deploy. Set your environment variables in the Render dashboard.</p><h2>Deploy to Railway</h2><p>A <code>railway.json</code> config is also included. Connect your repo and set environment variables in the Railway dashboard.</p><h2>Deploy to Fly.io</h2><p>A <code>fly.toml</code> is included for Fly deployments. Run <code>fly launch</code> and follow the prompts.</p><h2>Environment variables</h2><p>See <code>.env.example</code> for the full list of required variables. The most important are <code>DATABASE_URL</code>, <code>DJANGO_SECRET_KEY</code>, <code>STRIPE_LIVE_SECRET_KEY</code>, and your email credentials.</p>"}]),
            ]
            for title, slug, body in doc_pages:
                dp = DocsPage(title=title, slug=slug, body=body)
                getting_started.add_child(instance=dp)
                dp.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"  ✓ Docs section with {len(doc_pages)} pages created"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo site loaded successfully."))
        self.stdout.write(self.style.SUCCESS("Visit http://localhost:8000/ to see it."))
        self.stdout.write("")
        self.stdout.write("Pages created:")
        self.stdout.write("  /           → Home page")
        self.stdout.write("  /about/     → About")
        self.stdout.write("  /pricing/   → Pricing")
        self.stdout.write("  /contact/   → Contact")
        self.stdout.write("  /blog/      → Blog (with 3 sample posts)")
        self.stdout.write("  /docs/      → Documentation (with getting started section)")