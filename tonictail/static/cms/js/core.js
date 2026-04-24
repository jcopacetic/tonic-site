// Module: MODULE_NAME
// Description: DESCRIPTION_HERE
// Author: Jonathan Sumner | jonathan@khaoticdigital.com
//
// HOW TO USE THIS SCAFFOLD:
//   1. Replace every instance of MODULE_NAME with your module's snake_case name
//   2. Replace DESCRIPTION_HERE with a one-line description
//   3. Delete content fields you don't need; add the ones you do
//   4. The style and advanced groups are complete — only add to them, don't restructure
//   5. Import additional field sets from module-style-fields.js as needed

const {
  backgroundFields,
  sectionSpacingFields,
  containerWidthField,
  headingColorFields,
  textAlignField,
  // borderFields,       // Uncomment if module has card/border controls
  // layoutColumnsField, // Uncomment if module has a column-count picker
} = require('../../js/module-style-fields.js');

module.exports = [

  // ─── CONTENT GROUP ───────────────────────────────────────────────
  {
    type: 'group',
    name: 'content',
    label: 'Content',
    tab: 'CONTENT',
    children: [

      // ── Section intro ──────────────────────────────────────────
      {
        type: 'text',
        name: 'eyebrow',
        label: 'Eyebrow Label',
        help_text: 'Small label displayed above the heading. Great for category or section context. Leave blank to hide.',
        placeholder: 'Our Services',
        default: ''
      },
      {
        type: 'text',
        name: 'heading',
        label: 'Heading',
        help_text: 'Primary heading for this section.',
        placeholder: 'Section heading goes here',
        default: 'Section Heading'
      },
      {
        type: 'choice',
        name: 'heading_tag',
        label: 'Heading HTML Tag',
        help_text: 'Choose the correct heading level for your page hierarchy. H1 is for the page title only; use H2 for the first section heading, H3 for nested headings.',
        choices: [
          ['h1', 'H1'],
          ['h2', 'H2'],
          ['h3', 'H3'],
          ['h4', 'H4'],
        ],
        default: 'h2'
      },
      {
        type: 'text',
        name: 'subheading',
        label: 'Subheading / Body Copy',
        help_text: 'Supporting text displayed below the heading. Keep to 1–2 sentences. Leave blank to hide.',
        placeholder: 'A brief description that supports the heading above.',
        default: ''
      },

      // ── Repeater ───────────────────────────────────────────────
      // DELETE this group if this module has no repeating items
      {
        type: 'group',
        name: 'items',
        label: 'Items',
        help_text: 'Add, remove, or reorder items using the controls below.',
        occurrence: { min: 1, max: 12, default: 3 },
        children: [
          {
            type: 'image',
            name: 'image',
            label: 'Image',
            help_text: 'Upload or select an image for this item. Recommended: 800×600px, JPG or WebP.',
            default: {
              alt: '',
              src: ''
            },
            responsive: true,
            resizable: true
          },
          {
            type: 'text',
            name: 'eyebrow',
            label: 'Item Eyebrow',
            help_text: 'Small label above the item title.',
            placeholder: 'Category',
            default: ''
          },
          {
            type: 'text',
            name: 'title',
            label: 'Item Title',
            help_text: 'Heading for this item.',
            placeholder: 'Item title',
            default: 'Item Title'
          },
          {
            type: 'text',
            name: 'description',
            label: 'Description',
            help_text: 'Short description for this item. 1–3 sentences works best.',
            placeholder: 'A short description of this item.',
            default: ''
          },
          {
            type: 'group',
            name: 'link',
            label: 'Link',
            help_text: 'Optional link for this item.',
            children: [
              {
                type: 'text',
                name: 'label',
                label: 'Link Label',
                placeholder: 'Learn more',
                default: 'Learn more'
              },
              {
                type: 'link',
                name: 'url',
                label: 'Link URL',
                help_text: 'Where this link goes. Leave blank to hide the link.',
                default: {
                  url: { href: '', type: 'EXTERNAL' },
                  open_in_new_tab: false
                }
              }
            ]
          }
        ]
      },
      // ── End repeater ───────────────────────────────────────────

      // ── CTAs ───────────────────────────────────────────────────
      {
        type: 'group',
        name: 'cta_primary',
        label: 'Primary CTA Button',
        help_text: 'Main call-to-action button. Leave the URL blank to hide the button.',
        children: [
          {
            type: 'text',
            name: 'label',
            label: 'Button Label',
            placeholder: 'Get started',
            default: 'Get started'
          },
          {
            type: 'link',
            name: 'url',
            label: 'Button URL',
            default: {
              url: { href: '', type: 'EXTERNAL' },
              open_in_new_tab: false
            }
          }
        ]
      },
      {
        type: 'group',
        name: 'cta_secondary',
        label: 'Secondary CTA Button',
        help_text: 'Optional secondary button. Leave the URL blank to hide.',
        children: [
          {
            type: 'text',
            name: 'label',
            label: 'Button Label',
            placeholder: 'Learn more',
            default: 'Learn more'
          },
          {
            type: 'link',
            name: 'url',
            label: 'Button URL',
            default: {
              url: { href: '', type: 'EXTERNAL' },
              open_in_new_tab: false
            }
          }
        ]
      },

      // ── Accessibility ──────────────────────────────────────────
      {
        type: 'text',
        name: 'aria_label',
        label: 'Section ARIA Label',
        help_text: 'Describes this section to screen readers. Defaults to "Content section" if left blank. Use a short description like "Services overview" or "Client testimonials".',
        placeholder: 'Services overview',
        default: ''
      }

    ]
  },

  // ─── STYLE GROUP ─────────────────────────────────────────────────
  {
    type: 'group',
    name: 'style',
    label: 'Style',
    tab: 'STYLE',
    children: [

      // From module-style-fields.js — background type, color, gradient, image, overlay
      ...backgroundFields,

      // Section dividers
      {
        type: 'boolean',
        name: 'show_top_divider',
        label: 'Top Divider',
        help_text: 'Show a border line at the top of this section.',
        default: false
      },
      {
        type: 'boolean',
        name: 'show_bottom_divider',
        label: 'Bottom Divider',
        help_text: 'Show a border line at the bottom of this section.',
        default: false
      },
      {
        type: 'color',
        name: 'divider_color',
        label: 'Divider Color',
        help_text: 'Color of the top or bottom divider line. Defaults to the global border color.',
        default: {
          color: '/* [hubl-value] */',
          opacity: 100
        },
        display_conditions: [
          {
            controlling_field_path: 'style.show_top_divider',
            operator: 'EQUAL',
            controlling_value: 'true'
          }
        ]
      },

      // From module-style-fields.js — desktop and mobile padding groups
      ...sectionSpacingFields,

      // From module-style-fields.js — container width dropdown
      ...containerWidthField,

      // From module-style-fields.js — heading + subheading color pickers
      ...headingColorFields,

      // From module-style-fields.js — left / center / right
      ...textAlignField,

      // Button controls
      {
        type: 'choice',
        name: 'button_alignment',
        label: 'Button Alignment',
        help_text: 'Horizontal alignment of the CTA button(s).',
        choices: [
          ['left',   'Left'],
          ['center', 'Center'],
          ['right',  'Right']
        ],
        default: 'left'
      },
      {
        type: 'choice',
        name: 'button_size',
        label: 'Button Size',
        help_text: 'Controls the padding and font size of the CTA buttons in this section.',
        choices: [
          ['sm', 'Small'],
          ['md', 'Medium'],
          ['lg', 'Large']
        ],
        default: 'md'
      },

      // ── ADD MODULE-SPECIFIC STYLE FIELDS BELOW ─────────────── //
      // Uncomment from imports at top and add here as needed:
      //   ...borderFields
      //   ...layoutColumnsField

    ]
  },

  // ─── ADVANCED GROUP ──────────────────────────────────────────────
  {
    type: 'group',
    name: 'advanced',
    label: 'Advanced',
    tab: 'ADVANCED',
    children: [
      {
        type: 'text',
        name: 'custom_class',
        label: 'Custom CSS Class',
        help_text: 'Add one or more CSS classes to the outer module wrapper. Separate multiple classes with a space. For developer use.',
        placeholder: 'my-class another-class',
        default: ''
      },
      {
        type: 'text',
        name: 'anchor_id',
        label: 'Section Anchor ID',
        help_text: 'Creates a bookmark anchor for linking directly to this section. Enter without the # character — for example, type "contact" to create a link target for #contact.',
        placeholder: 'contact',
        default: ''
      },
      {
        type: 'boolean',
        name: 'hide_on_mobile',
        label: 'Hide on Mobile',
        help_text: 'When enabled, this module will not be visible on screens smaller than 768px.',
        default: false
      }
    ]
  }

];