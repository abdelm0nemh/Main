# abdelmonemhassan.com: SEO, AI visibility and repair pass (2026-10-19)

The AdvanSEM playbook, adapted for a personal brand: one person, not an agency.
Everything below is live unless marked **draft**. Backups of everything changed are on the server in
`/home/qyh52kbjm5j7/private-backups-moved-from-public_html/` (outside the public web folder).

## Security (fixed first)
- `APP-DATA.SQL`, a full 6 MB database dump from May 2024, was publicly downloadable from the site root,
  together with `APP-META.INI` and an old `.htaccess` copy. All three were moved out of `public_html` (kept, not deleted).
- `.htaccess` now refuses `.sql/.bak/.ini/.log/.env` files, `error_log`, `readme.html`, `license.txt`, and directory listings.
- The public REST user list (`/wp-json/wp/v2/users`) is hidden from logged-out visitors.

## Search and AI visibility (`growth-child/inc/monem-seo.php`)
- One `Person` entity for Abdelmonem Hassan: real photo (was a Gravatar placeholder), alternate names
  (Monem, Abdelmonem H., عبدالمنعم حسن), job title, skills, languages, education, 11 certificates, and profile links.
  AIOSEO's duplicate author `Person` is folded into it, so every post and page points at the same person.
- Website name fixed (AIOSEO printed "Abdelmonem Hassan - Abdelmonem Hassan").
- About page is a `ProfilePage`; the home page is `about` the person.
- `Service` + `OfferCatalog` (USD prices) on the three media buying package pages, read live from the pricing widgets.
- `FAQPage` from any visible Elementor accordion/toggle, or from a post's `_monem_faq` meta.
- `/llms.txt` is now generated live: who he is, key facts, every package and price, case studies, all articles.
- AIOSEO: explicit Facebook, Instagram and LinkedIn URLs (it was guessing X, TikTok and Pinterest URLs from one username);
  sitemap limited to posts, pages, portfolio and categories (attachments, 447 thin tag archives and old product types removed);
  tag archives set to noindex.
- noindex: Meeting Schedule (duplicate of /consultation/) and the older Media Buying Packages page (duplicate tiers and old Stripe links).

## Headings, content and media
- Every page now has one H1: the theme printed page and post titles as H3, and the home hero name as H2.
  Pages whose content already has its own H1 keep the title as H3.
- Blog heading "News Feeds" is now "Media Buying & Marketing Blog".
- 70 of 72 posts were "Uncategorized". They now sit in 8 topic categories with descriptions.
- One post that missed its schedule a year ago (Unlock the Secrets to Driving Organic Traffic) is published, with a featured image.
- Alt text: 117 images had none; 110 in-post images and their media items carried full AI image prompts (up to 600+ characters).
- Meta titles and descriptions rewritten for Home, About, Services, the 3 package pages, Portfolio, Contact and Blog.
  "100% job success rate" was dropped from the home description until it is re-checked on Upwork.
- Author box under every post (photo, bio from Users > Profile, consultation button).

## Repairs
- Elementor warning logged ~940 times a day ("display_name on false"): 135 items belonged to a deleted user; reassigned.
- Contact form: the message box was raw HTML, not a form field, so it was never validated; now a real field.
  Duplicate "Email Marketing" option removed, "FBA" is "Amazon FBA", budget asks for a monthly ad budget.

## Drafts for you to review (not live)
- **Home – FAQ v1** (page 4531): the live home page plus an 11-question FAQ section (price, platforms, ad spend,
  minimum budget, timeline, reporting, account ownership, location, consultation, Upwork) and a consultation button.
- **3 articles** written from the topics you post about in Arabic (ideas only, no videos):
  4532 reading competitor ads in Meta Ad Library / TikTok Creative Center / Google Ads Transparency Center,
  4533 creative fatigue, 4534 cheap vs quality leads. Each has a meta description, category, image and FAQ schema.

## Round 2 (same day, on Monem's go-ahead)
- FAQ section (11 questions) added to the live home page (page 28) rather than swapping the front page,
  so the menu link, SEO settings and translations stay attached. Previous layout saved in the
  `_monem_elementor_backup_20261019` meta and the server backup folder; the draft copy (4531) is now private.
- The 3 articles are published.
- Arabic: the machine translation spelled the name "مونيم"; it is now "منعم". The home title, FAQ heading and
  questions, bio and About description now use "ميديا باير", marked as reviewed in TranslatePress.
- Comments: all 67 ever received were spam waiting in moderation. They are in the spam folder, and comments
  and pingbacks are closed on posts and pages.
- Plugin updates, one at a time with a folder backup and an automatic rollback check: Limit Login Attempts 3.3.10,
  MC4WP 4.14.1, Koalendar 1.0.6, Setmore 12.8, Site Kit 1.189.0, Redux 4.5.16 (theme options verified
  unchanged), CMB2 2.13.4. Backups: `private-backups-moved-from-public_html/plugins-before-update/`.
- Left for a supervised update: Elementor 4.1.4 → 4.3.5, AIOSEO 4.9.10 → 5.0.3, TranslatePress 3.2.3 → 3.3.8
  (larger changes that can affect layout or settings), and WPS Hide Login (controls the login URL).

## Round 3: remaining plugin updates (TranslatePress deliberately left alone)
Safety net taken first: full database dump (`private-backups-moved-from-public_html/db-before-plugin-updates/`),
a separate dump of the AIOSEO tables and options, a copy of each plugin folder, and a rendered snapshot of
19 pages (EN/AR/ES): headings, every Elementor widget, images, links, forms, iframes, Stripe links, schema,
title, description, canonical, robots and all visible text. Two snapshots in a row matched exactly.
- Elementor 4.1.4 → 4.3.5: `wp elementor update db` ran only its per-version step (no data migration), CSS regenerated.
  Elementor settings unchanged; all 15 Growth theme widgets still registered.
- AIOSEO 4.9.10 → 5.0.3: all 591 per-page SEO rows, all settings, robots.txt, sitemaps and llms.txt identical;
  the child theme's schema, robots and sitemap filters still apply.
- WPS Hide Login 1.9.19 (custom login URL verified before and after), Akismet 5.7.2 and Disabled Source 1.8.3 (both inactive).
- Result against the original snapshot: no difference on any page except that Elementor now labels its
  heading/image/divider stylesheets as separate files (the same files were loaded before).
- Log entries during the update window: one AIOSEO fatal and two warnings at the moment its files were being
  replaced, and one Elementor cron notice during its DB step; none recur.
- Elementor 4.3 bundles the WordPress MCP Adapter, whose default server logged 3 errors on every REST request.
  Turned off with `add_filter( 'mcp_adapter_create_default_server', '__return_false' );` in growth-child/functions.php;
  Elementor's own MCP server and the Novamira connector are unaffected. Log is clean since.

## Needs your decision or input
1. Confirm these FAQ answers before publishing: campaigns run in the client's own ad accounts; ad spend is paid
   to the platform, not included in the fee; first 2–4 weeks are testing; you audit tracking before spending.
2. Re-check "Top 3%" and "100% Job Success" on Upwork; a public listing for "Monem H." shows 4.9 stars from 36 reviews.
3. Location: LinkedIn says Florida, United States; the site says remote, worldwide. Pick one and use it everywhere.
4. Update the TranslatePress Business add-on (1.6.3 against core 3.2.3); it logs warnings from its language popup.
5. Test the Stripe "Purchase Now" links; they cannot be checked from the server.
6. Submit `sitemap.xml` in Google Search Console and Bing Webmaster Tools.
7. Comments are open on posts with no spam filter (Akismet is inactive).
8. Optional: link your Person entity to AdvanSEM as founder, or keep the two fully separate.
