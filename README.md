# Daughters of Legends Exact Live Site + Added Subdomains

This prototype keeps the current https://daughtersoflegends.org/ homepage exact by embedding the live website in index.html.

Added feature areas:
- ai.html -> ai.daughtersoflegends.org
- membership.html -> members.daughtersoflegends.org
- events.html -> events.daughtersoflegends.org
- community.html -> community.daughtersoflegends.org
- news.html -> news.daughtersoflegends.org
- newsletter.html -> newsletter.daughtersoflegends.org
- studio.html -> studio.daughtersoflegends.org

Shop was not added as a new subdomain because the user requested all subdomains except shop.

Important: index.html requires internet because it displays the live daughtersoflegends.org website in an iframe.


V2 update:
- Removed the side "Platform Areas" button/drawer from the homepage.
- Added a permanent top navigation bar above the live original website.
- Top navigation includes: Home, AI Coach, Membership, Events, Community, News + Blog, Newsletter, Content Studio.
- Shop is still excluded.
- Because the homepage is still the live current website in an iframe, this top navigation is added around the live site rather than editing the remote site's internal WordPress menu.


V3 update:
- Removed the extra white top navigation bar.
- Removed the side platform drawer.
- Added one black/purple navigation bar styled like the original site navigation.
- Replaced the old-style menu labels with AI Coach, Membership, Events, Community, News + Blog, Newsletter, and Content Studio.
- Cropped the live iframe so the original site's duplicated internal nav is hidden beneath the custom single nav.


V4 update:
- Revised every subdomain page to match the dark original site style.
- Same single black/purple navigation bar appears on the homepage and every subdomain page.
- Updated colors, background, text colors, typography scale, spacing, and section style to match the screenshot.
- Removed the bright white card/subdomain page feel.


V5 update:
- Removed News + Blog subdomain from navigation and replaced it with Shop.
- Removed Community subdomain from navigation and added Our Bylaws.
- Added Home back to the nav.
- Our Bylaws opens the live homepage at the bylaws anchor.
- Removed the large image block from all custom subdomain pages.
- Membership now has tiers, prices, and perks.
- Events now has mock events with sign-up links.
- Newsletter now has multiple full-length update pieces and a join-the-update-list form.
- Content Studio now has more DOLSTV content and no large hero photo.

## Context assembly and store integrity

The backend separates retrieval, context assembly, store auditing, ingestion, and HTTP handling into independent modules:

- [retrieval.py](legacy-ai-coach/backend/retrieval.py): corpus-aware passage ranking, deduplication, and page diversity.
- [context.py](legacy-ai-coach/backend/context.py): bounded reference context with stable passage identities, explicit source pages, and inspectable lexical coverage.
- [store_audit.py](legacy-ai-coach/backend/store_audit.py): page/text checks, duplicate warnings, finite embedding checks, and embedding-dimension consistency.
- [app.py](legacy-ai-coach/backend/app.py): validated chat requests, bounded retrieved context, source excerpts, and demo/model response paths.
- [ingest.py](legacy-ai-coach/backend/ingest.py): PDF cleaning, overlapping chunks, embedding batches, integrity checks, and atomic publication.

The passages sent to the model are the same bounded selection used to populate response sources. Context excerpts are represented as JSON reference records; the system prompt treats their contents as reference material rather than instructions. Passage/source metadata is preserved without inventing page numbers. Store audits run before serving a loaded store and before publishing newly ingested chunks.

```sh
cd legacy-ai-coach/backend
python -m unittest discover -s tests -v
```

Tests cover context limits, stable identities, duplicate suppression, query overlap, invalid metadata, nonfinite or inconsistent embeddings, HTTP request validation, and mocked embedding responses. Live model calls and PDF ingestion require the configured service credentials and authorized source document; the tests make no paid API requests. Lexical coverage is not a calibrated correctness probability.
