# Live runbook: first run on Tableau Cloud and Snowflake

Nothing here has been done yet. Credentials go in environment variables only; never in files, chat or git.

1. **Tableau sandbox.** Join the Tableau Developer Program (free) and request a Tableau Cloud site. Create a Personal Access Token (Settings, Personal Access Tokens).
2. **Snowflake.** Start a free trial. Create `TABGOV_DB`, schema `MART`, and a read-only role for Tableau.
3. **Load data.** Load Complete Journey `transaction_data.csv` and `product.csv` into `raw_transactions` and `raw_product`; run `sql/mart.sql`.
4. **Publish.** In Tableau Desktop (or Public) connect to Snowflake, publish one extract-based data source per mart view to the Certified project, build three workbooks, schedule daily extract refreshes.
5. **Plant a few real defects on purpose** (a copy of a source, a stale workbook, a user-level grant) so detection can be checked against what you know.
6. **Export settings:** `TABLEAU_URL`, `TABLEAU_SITE`, `TABLEAU_PAT_NAME`, `TABLEAU_PAT_SECRET`; `pip install -e .[live]`.
7. **Run** `client.connect()` then `client.normalise(...)` and `detect.run_all`; compare with what you planted and fix any adapter field that differs. Record the result in `MODEL_CARD.md`; until then keep the live claim out of the CV.
