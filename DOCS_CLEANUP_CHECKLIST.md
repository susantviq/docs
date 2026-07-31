# viq-docs cleanup checklist

**Created:** 24 Jul 26
**Purpose:** clear the accumulated drift in the connector documentation before starting the AIOS / Vortex Runtime connector sync work.
**Status of counts below:** every number was verified against the live repos on 24 Jul 26, not taken from an existing doc.

---

## Ground truth, measured today

Use these numbers. Do not copy figures from other pages, they are the thing being fixed.

| Fact | Value | How it was measured |
|---|---|---|
| Connector manifests (engine layer) | **220** | `ls config/vortex_mind/manifests/*.yaml` |
| Catalog rows (catalog layer) | **193** | distinct `'key' =>` in `database/seeders/*.php` |
| Compiled KPI cards | **7,491** | `card_registry.json` and the `vm_cards` table, both agree |
| Connector doc directories | **225** | `nerve-centre/kpi-cards/*/` excluding `concepts` |
| Individual card pages | **7,328** | `.mdx` under `kpi-cards/` minus index/audit/sentiment/concepts |
| Archetypes | **22** | `ls config/vortex_mind/archetypes/*.yaml` |

### Decision needed before Batch B

The docs quote a single "connectors" number, but there are two legitimate answers: **220** (manifests, the things that produce KPI cards) and **193** (catalog rows, the things a user sees on the connect page). These layers are genuinely different and conflating them is the most common source of confusion in this codebase.

**Recommendation:** the public number is **220**, because every page quoting it is describing KPI cards, audits and the Nerve Centre, all of which are engine-layer concepts. Write the chosen definition into the glossary so the next person does not re-litigate it.

---

## Batch A: delete stale content

**Why first:** this is the largest single reduction in drift, it is low risk, and it makes Batch D almost disappear. Roughly 15% of the connector doc tree describes connectors that exist in neither the manifest set nor the catalog table.

### A1. Delete 34 stale connector directories

Verified absent from **both** `config/vortex_mind/manifests/` and the connector seeders. Each is a whole directory under `nerve-centre/kpi-cards/`.

- [ ] `aircall`
- [ ] `app-dynamics`
- [ ] `bluesnap`
- [ ] `bugsnag`
- [ ] `chargebee`
- [ ] `checkout-com`
- [ ] `dialpad`
- [ ] `dynatrace`
- [ ] `eway`
- [ ] `fastly`
- [ ] `gocardless`
- [ ] `heap`
- [ ] `helcim`
- [ ] `kissmetrics`
- [ ] `logrocket`
- [ ] `looker`
- [ ] `lucidchart`
- [ ] `mailgun`
- [ ] `miro`
- [ ] `mode-analytics`
- [ ] `moosend`
- [ ] `mural`
- [ ] `nuvei`
- [ ] `omnisend`
- [ ] `postmark`
- [ ] `raygun`
- [ ] `recharge`
- [ ] `recurly`
- [ ] `ringcentral`
- [ ] `rollbar`
- [ ] `sparkpost`
- [ ] `stax-payments`
- [ ] `tableau`
- [ ] `vonage`

**Before deleting:** confirm with the connector team that none of these are imminent builds. If any is genuinely planned, keep the directory and add a `status: planned` note to its `index.mdx` rather than leaving it looking shipped.

**After deleting:** remove every corresponding entry from `docs.json` and add a redirect for any page that has been publicly linked. There are already 26 redirects in `docs.json`, follow that pattern.

### A2. Rename 3 directories to match the manifest key

These are not stale, they are the same connector under a different slug. Renaming removes a false gap in both directions.

- [ ] `brevo-sendinblue` becomes `brevo` (manifest key is `brevo`)
- [ ] `customerio-api` becomes `customer-io` (manifest key is `customer_io`)
- [ ] `mixpanel-b` merges into `mixpanel` (duplicate; keep whichever content is better, delete the other)

Each rename needs its `docs.json` entries updated and a redirect from the old path.

### A3. `amazon`: resolved, merged into `amazon-seller`

Settled on evidence rather than judgement. Both directories were matched against the 60 compiled `amazon_seller` cards, allowing for the two different slug conventions (`amazon` drops the parenthetical, `amazon-seller` keeps it, so `negative-feedback` and `negative-feedback-30d` are the same card):

| Directory | Pages | Real cards covered | Pages with no card behind them |
|---|---|---|---|
| `amazon` | 71 | 60 of 60 | **12** |
| `amazon-seller` | 59 | 60 of 60 | **0** |

Both covered every real card, so nothing was lost by choosing. `amazon-seller` is the exact set; `amazon` carried 12 pages for metrics the connector never produces (`avg-review-rating`, `buyer-messages-unread`, `dispute-rate`, `fees-as-of-revenue`, `listing-quality-score`, `listings-expiring-soon`, `marketplace-fees-paid`, `out-of-stock-listings`, `pending-payouts`, `seller-feedback-score`, `top-listings-by-revenue`, `total-transactions`).

Corroborated in code: the live integration type is `amazon_sp`, and every resolution site normalises it to the `amazon_seller` manifest (`AuditOrchestrator.php:1225`, `ManifestDrivenGraphBuilder.php:799`).

- [x] Deleted `amazon` (72 pages) and redirected it to `amazon-seller`.
- [x] Carried the human-authored positioning prose across, dropping its incorrect "77 KPI pulses" claim (the real figure is 60).

---

## Batch B: fix every connector and card count

**20 locations.** All are simple string edits. Apply the Batch A decision on 220 first.

### B1. Card count: 6,034 becomes 7,491

- [ ] `ask-viq/overview.mdx:15`
- [ ] `ask-viq/overview.mdx:25`
- [ ] `ask-viq/profiles.mdx:82` ("the 6,034-card catalogue")
- [ ] `get-started/glossary.mdx:71`
- [ ] `index.mdx:38`
- [ ] `nerve-centre/overview.mdx:4` (frontmatter description)
- [ ] `nerve-centre/overview.mdx:11`
- [ ] `nerve-centre/overview.mdx:51`
- [ ] `nerve-centre/kpi-cards.mdx:13`
- [ ] `nerve-centre/kpi-cards/concepts/hero-cross-channel-tiers.mdx:6`
- [ ] `nerve-centre/kpi-cards/concepts/kpi-model.mdx:3` (frontmatter description)
- [ ] `nerve-centre/kpi-cards/concepts/kpi-model.mdx:6`
- [ ] `nerve-centre/kpi-cards/concepts/kpi-model.mdx:63`
- [ ] `nerve-centre/kpi-cards/concepts/kpi-model.mdx:115`
- [ ] `nerve-centre/kpi-cards/concepts/kpi-model.mdx:116`

### B2. Connector count: everything becomes 220

- [ ] `get-started/introduction.mdx:74` says "215 integrations"
- [ ] `get-started/quickstart.mdx:176` says "215 integrations in total"
- [ ] `integrations/connector-catalogue.mdx:7` says "239 connectors across 19 categories" (overstated by 19)
- [ ] `nerve-centre/connectors.mdx:9` says "240+ data sources" (overstated by 20)
- [ ] `actions/overview.mdx:7` says "200+ connectors"
- [ ] `ask-viq/overview.mdx:15` and `:25` say "200+ connectors"
- [ ] `get-started/glossary.mdx:41` says "200+ connectors"
- [ ] `index.mdx:38` says "200+ connectors"
- [ ] `nerve-centre/overview.mdx:11` and `:87` say "200+ connectors"
- [ ] `nerve-centre/kpi-cards/concepts/index.mdx:7` says "200+ connectors"
- [ ] `nerve-centre/kpi-cards/concepts/kpi-model.mdx:3`, `:6`, `:63` say "over 200" / "215"

### B3. Category count is contradictory

Three different numbers are in circulation: "11 connector types", "19 categories", and the navigation itself now renders **16** category groups.

- [ ] `nerve-centre/overview.mdx:4`, `:11`, `:21` all say "11 connector types" and there is a whole section headed "The 11 connector types"
- [ ] `integrations/connector-catalogue.mdx:7` says "19 categories"
- [ ] Decide the real number, then fix both. Note the manifests themselves have near-duplicate category strings that should be merged first (see F3), because that changes the answer.

---

## Batch C: write the 31 missing connector pages

These connectors have a shipped manifest and no documentation directory at all. Grouped so they can be assigned as coherent chunks.

**Cloud and data warehouse (6)**
- [ ] `aws`
- [ ] `azure`
- [ ] `gcp`
- [ ] `bigquery`
- [ ] `redshift`
- [ ] `cloudhub_insights`

**Databases (8)**
- [ ] `cassandra`
- [ ] `dynamodb`
- [ ] `firestore`
- [ ] `mssql`
- [ ] `neo4j`
- [ ] `oracle`
- [ ] `planetscale`
- [ ] `sqlite`

**AI providers (3)**
- [ ] `anthropic`
- [ ] `openai`
- [ ] `gemini`

**Finance and accounting (5)**
- [ ] `freshbooks`
- [ ] `quickbooks_api`
- [ ] `wave`
- [ ] `xero_api`
- [ ] `zoho_books`

**Productivity and no-code (4)**
- [ ] `airtable`
- [ ] `baserow`
- [ ] `coda`
- [ ] `google_sheets`

**Other (5)**
- [ ] `github`
- [ ] `google_tag_manager`
- [ ] `email` (see D2, this is a notification channel so it needs the channel page shape, not a card set)
- [ ] `wrike` (note: `wrike-api` is documented, `wrike` is a separate manifest, confirm whether both should exist)
- [ ] `microsoft_teams` (see the flagged AIOS issue below, resolve that first)

---

## Batch D: the audit page gap is mostly not a gap

44 connector directories are missing `audit.mdx` and `sentiment.mdx`, which sounds alarming. It is not.

- **37** of the 44 are stale directories being deleted in Batch A. They resolve themselves.
- **6** are notification channels that **correctly** have no audit: `discord`, `pushover`, `slack`, `teams`, `telegram`, `twilio`. Under the rule just agreed, channels get a health check only and never an audit profile.
- **1** is `amazon`, the catalog-only page from A3.

So there is effectively **zero real audit-documentation debt.** The work is not writing 44 pages, it is:

- [ ] **D1.** Complete Batch A, then re-run the check. Expect exactly 7 remaining.
- [ ] **D2.** Write the channel rule down somewhere permanent, ideally in `nerve-centre/connectors.mdx` and the glossary. Proposed wording:

  > Connectors fall into two classes. **Data sources** hold auditable state (stores, ad accounts, payments, analytics) and carry KPI cards plus an audit profile. **Channels** are where agents send and receive messages (Slack, Teams, Telegram, Discord, Twilio, Pushover, email). Channels are health-checked, never audited, and carry no business KPI cards. A channel may show connection-health cards, for example whether a webhook is configured and which host it points at, but never business metrics.

- [ ] **D3.** Confirm the email service providers are documented as data sources, not channels. **Agreed ruling: SendGrid and the other ESPs keep their KPI cards.** Only the notification channels lose them. SendGrid currently has 32 card pages and Mailgun 30, which is correct behaviour, though Mailgun's directory is being deleted in Batch A as it has no manifest.

---

## Batch E: setup and authentication documentation

**The biggest real gap, and the one that matters most for a source-available Runtime release.**

Only **10 of 220** connectors have a setup page under `integrations/`: shopify, bigcommerce, adobe-commerce, google-ads, meta-ads, tiktok-ads, stripe, paypal, netsuite, plus the catalogue index.

The per-connector `kpi-cards/*/index.mdx` pages describe what the cards mean but contain no authentication or connection instructions. For the cloud product that is survivable because the connect form guides the user. For a locally installed Runtime where users supply their own credentials, it is not.

- [ ] **E1.** Agree a minimum setup-page template: what credentials are needed, where in the vendor's console to obtain them, which scopes and why they are read-only, and what to do when the connection fails.
- [ ] **E2.** Prioritise by the Runtime's own scope: the ecommerce platforms and ad platforms first, since those are the ones getting runtime audit profiles.
- [ ] **E3.** Decide whether these live under `integrations/` (current pattern, separate tree) or as a `setup.mdx` inside each `kpi-cards/<connector>/` directory (co-located, easier to keep in sync). Co-locating is probably right now that there are 225 connector directories.

---

## Batch F: repo hygiene

- [ ] **F1. Find the page generator.** The `HUMAN_AUTHORED` fences and 181 structurally identical audit pages prove a generator exists outside this repo. Locate it, commit it here, and document how to run it. **Everything above will silently re-drift without this**, and adding a second product's connector tree by hand to a 762 KB `docs.json` is not viable. Treat this as the real blocker.
- [ ] **F2. Write a README and CONTRIBUTING.** There is currently neither. `AGENTS.md` is 40 lines of unedited Mintlify boilerplate with the placeholder comments still in it and says nothing about connectors, cards or navigation. At minimum: how to add a connector page, how to regenerate nav, and the two-layer connector model.
- [ ] **F3. Merge near-duplicate category strings in the manifests.** The engine side has both "Social Media" (3) and "Social" (2), "Shipping & Delivery" (21) and "Shipping" (1), "Notifications" (8) and "Notification Channels" (2), plus a "Fulfillment" spelling. These propagate into the docs taxonomy and are part of why the category count is disputed. This is an AIOS fix that unblocks B3.
- [ ] **F4. Fix the two orphan pages.** `index.mdx` and `nerve-centre/kpi-cards.mdx` exist on disk but are not in `docs.json` navigation. The latter is real content reachable only by direct link.
- [ ] **F5. Add a counts test.** Once F1 lands, have the generator emit the connector and card counts into a single included snippet so no page ever hardcodes them again. This is what prevents Batch B recurring.

---

## Flagged for the AIOS team, not docs work

Found while diffing the two repos. These are app-side defects that affect what the docs should say, so they should be resolved before the affected pages are written.

- [ ] **Duplicate Microsoft Teams manifests.** `teams.yaml` (`notification_channel`, `action_channel`, status `planned`, 0 cards) and `microsoft_teams.yaml` (`collaboration_activity`, `data_pull`, status **live**, **21 cards**) both exist and **alias each other**: `teams.yaml` declares `type_aliases: [microsoft_teams, ms_teams]` while `microsoft_teams.yaml` declares `type_aliases: [teams]`. Whichever loads first wins the alias map.

  This directly affects the channel ruling. Teams is on the "communication channel, no KPIs" list, but the live manifest is a 21-card collaboration data source. Somebody needs to decide which Teams is real before the docs can describe it.

- [ ] **Duplicate Wrike manifests.** `wrike.yaml` (32 cards) and `wrike_api.yaml` (24 cards, declares `type_aliases: [wrike]`). Believed intentional, the OAuth flow differs from the API-token flow, but only `wrike-api` is documented and the alias overlap has the same shadowing risk.

---

## Suggested order

1. **F1** find the generator. Everything else is throwaway hand-work without it.
2. **A** delete and rename. Largest drift reduction, lowest risk, and it collapses Batch D.
3. **B** fix the counts, once the 220-versus-193 definition is agreed.
4. **D2** write down the channel rule. Small, and it is the thing being encoded in the manifest schema at the same time.
5. **F3** merge the category strings on the AIOS side, then finish **B3**.
6. **C** write the 31 missing connector pages, generator-assisted.
7. **E** setup and auth pages, prioritised by the Runtime scope.
8. **F2, F4, F5** hygiene and the guard that stops this recurring.
