"""Adapter from live Tableau Cloud (REST + Metadata API) to the frames used by the detectors.

Status: written against the documented tableauserverclient and Metadata API shapes and tested
with fakes (tests/test_client.py). It has NOT been run against a live site from the build
environment; docs/LIVE_RUNBOOK.md covers the first live run. Credentials come from environment
variables only and are never stored.
"""
from __future__ import annotations
import os, pandas as pd

LINEAGE_QUERY = """
query { publishedDatasources { luid name projectName isCertified owner { luid }
  upstreamTables { fullName } workbooks { luid } }
  workbooks { luid name projectName owner { luid } views { name }
  upstreamDatasources { luid } } }
"""


def connect():  # pragma: no cover - needs a live site
    import tableauserverclient as TSC
    auth = TSC.PersonalAccessTokenAuth(os.environ["TABLEAU_PAT_NAME"], os.environ["TABLEAU_PAT_SECRET"],
                                       site_id=os.environ["TABLEAU_SITE"])
    server = TSC.Server(os.environ["TABLEAU_URL"], use_server_version=True)
    server.auth.sign_in(auth)
    return server


def _pager(endpoint):
    import tableauserverclient as TSC
    return list(TSC.Pager(endpoint))


def normalise(users, workbooks, datasources, jobs, tables, asof, usage=None, pager=list):
    """users/workbooks/datasources: iterables of TSC-like items; usage: {luid: (last_viewed, views_90d)}."""
    usage = usage or {}
    u = pd.DataFrame([dict(user_id=x.id, active=getattr(x, "site_role", "") != "Unlicensed") for x in users])
    d = pd.DataFrame([dict(ds_id=x.id, name=x.name, project=x.project_name, certified=bool(x.certified),
                           owner_id=x.owner_id, table=(getattr(x, "table", None) or ""),
                           custom_sql="", extract=True) for x in datasources])
    w = pd.DataFrame([dict(wb_id=x.id, name=x.name, project=x.project_name, owner_id=x.owner_id,
                           datasources=list(getattr(x, "datasource_ids", [])),
                           last_viewed=pd.Timestamp(usage.get(x.id, (pd.NaT, 0))[0]),
                           views_90d=int(usage.get(x.id, (pd.NaT, 0))[1])) for x in workbooks])
    r = pd.DataFrame([dict(ds_id=j.target_id, run_at=pd.Timestamp(j.completed_at),
                           status="Success" if j.finish_code == 0 else "Failed") for j in jobs])
    return dict(users=u, datasources=d, workbooks=w, runs=r, snowflake_tables=set(tables), asof=pd.Timestamp(asof),
                permissions=pd.DataFrame(columns=["content_id", "content_type", "grantee_type", "grantee", "capability"]),
                calcs=pd.DataFrame(columns=["wb_id", "name", "formula"]))


def lineage_from_graphql(payload: dict) -> dict:
    """Map a Metadata API response to {datasource luid: table} and {workbook luid: [datasource luids]}."""
    ds = {d["luid"]: (d["upstreamTables"][0]["fullName"] if d["upstreamTables"] else "")
          for d in payload["data"]["publishedDatasources"]}
    wb = {w["luid"]: [x["luid"] for x in w["upstreamDatasources"]] for w in payload["data"]["workbooks"]}
    return dict(datasource_table=ds, workbook_datasources=wb)
