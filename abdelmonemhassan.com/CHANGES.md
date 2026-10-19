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
