# Contributing to viq-docs

Mintlify docs site for Vortex IQ. No build step: `docs.json` is the navigation
and every page is an `.mdx` file listed in it.

## Before you open a PR

```bash
python bin/check-docs.py

# also check connector parity against the platform repo
python bin/check-docs.py --platform ../Agentic-workflow-SSO-LOGIN
```

It fails the build on the four things that have historically drifted: nav
entries pointing at deleted files, pages missing from nav, hardcoded catalogue
totals, and connector directories with no manifest behind them.

## The two layers, and which number is public

A connector exists in two independent places in the platform, and they are
counted differently. Getting these confused is the most common documentation
error.

| Layer | Where | What "live" means |
|---|---|---|
| **Catalog** | a row in the `connectors` table, seeded from `database/seeders/` | the connect card appears on Settings, Connected Sources. Produces no data on its own |
| **Engine** | `config/vortex_mind/manifests/<key>.yaml` plus a PHP runtime engine | produces the KPI cards, audits and alerts |

**The public number is the engine layer**, because every page that quotes it is
describing KPI cards, audits or the Nerve Centre, all of which are engine-layer
concepts. A connector with a catalog row but no manifest is not yet documented
as available.

## Never state an exact total

Counts change every time a connector ships or a card is added. A figure written
into 15 pages is 15 things to update and 15 chances to be wrong, which is
exactly what happened before July 2026.

- Write **"over 7,000 cards"**, not "7,491 cards".
- Write **"over 200 connectors"**, not "220 connectors".
- Approved qualifiers: `over`, `more than`, `about`, `around`, `upwards of`.

`bin/check-docs.py` enforces this for catalogue-wide totals. Per-connector
counts ("BigCommerce tracks 115 cards") are fine and useful, they live on
generated index pages and are regenerated with the content.

## Connector classes

Two classes, and the class decides whether the connector gets KPI cards.

- **Data source**: holds auditable state. Commerce, marketplaces, ads,
  payments, analytics, CRM, email marketing, shipping, monitoring, databases.
  Gets a full card set, an `audit.mdx`, and a `sentiment.mdx`.
- **Channel**: where Vortex IQ sends and receives messages. Slack, Microsoft
  Teams, Telegram, Discord, Twilio, Pushover, email. Gets an `index.mdx`
  describing the integration and **no KPI card pages, no audit page**.

A channel may document a small number of connection-health cards (is the
webhook configured, which host does it point at). Those are diagnostics, not
business metrics.

Email marketing platforms (Klaviyo, Mailchimp, Brevo, SendGrid) are **data
sources**, not channels. They measure campaign performance and revenue, so they
carry full KPI cards.

## Adding a connector

1. Confirm the connector has a manifest at
   `config/vortex_mind/manifests/<key>.yaml` in the platform repo. No manifest
   means no docs yet.
2. Create `nerve-centre/kpi-cards/<slug>/` where `<slug>` is the manifest
   `connector_key` with underscores replaced by hyphens. The slug must match,
   `check-docs.py` enforces it.
3. Add `index.mdx`. For a data source, also add `audit.mdx` and
   `sentiment.mdx`, plus one page per card.
4. Add every page to `docs.json` under the right category group inside
   `Documentation > The AI OS > Nerve Centre > KPI Cards`. Mintlify has no glob
   support, so each page is listed explicitly.
5. Run the checker.

### Renaming or removing a connector

Add a redirect for every path that moves. `docs.json` already has a `redirects`
array; use a wildcard at the connector level:

```json
{ "source": "/nerve-centre/kpi-cards/old-slug/:slug*",
  "destination": "/nerve-centre/kpi-cards/new-slug/:slug*" }
```

For a removed connector, point it at `/nerve-centre/connectors` so an old
inbound link still lands somewhere useful.

## Generated content and the HUMAN_AUTHORED fences

Card index pages and the `audit.mdx` / `sentiment.mdx` pages are generated from
the platform manifests. Hand-written prose inside them is wrapped so a
regeneration does not destroy it:

```mdx
{/* HUMAN_AUTHORED:landing_positioning */}
Your prose here survives regeneration.
{/* /HUMAN_AUTHORED:landing_positioning */}
```

**Only edit inside those fences** on a generated page. Anything outside them is
overwritten on the next run.

The generator itself does not currently live in this repo, which is a known gap:
find it or rebuild it before any large-scale page work, otherwise the edit is
hand-work that the next regeneration reverts.

## Style

- No em dashes, no en dashes. Use a comma, a colon, or a full stop. (There is
  pre-existing debt here, roughly 900 lines, which the checker warns about
  rather than failing on until it is swept.)
- "Ask Viq" is always two words. Never use the second word alone.
- "e-commerce" in prose, `ecommerce` only in code and slugs.
- Do not quote figures the platform cannot back.
