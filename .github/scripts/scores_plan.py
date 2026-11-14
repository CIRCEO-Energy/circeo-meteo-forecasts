"""Plan the scores jobs: every (product, month) whose forecast assets are newer than its score
file (or that has none). Prints the GitHub Actions matrix (max 250 entries, oldest first)."""
import json
import os
import re
import subprocess
import sys

REPO = os.environ.get("GITHUB_REPOSITORY", "boris-circeo/circeo-meteo-forecasts")
PRODUCTS = [  # release regex, file prefix, kind
    (r"gefs-oper-uv10-0p5-\d{4}", "gefs_oper_uv10_0p5", "wind"),
    (r"gefs-ctl-uv10-0p25-v2", "gefs_ctl_uv10_0p25", "wind"),
    (r"gefsv12-reforecast-uv10-0p5-v2", "gefs_reforecast_uv10_0p5", "wind"),
    (r"ecmwf-oper-uv10-0p25-v2", "ecmwf_oper_uv10_0p25", "wind"),
    (r"ecmwf-aifs-uv10-0p25-v2", "ecmwf_aifs_uv10_0p25", "wind"),
    (r"ecmwf-enfo-uv10-0p5-\d{4}", "ecmwf_enfo_uv10_0p5", "wind"),
    (r"ecmwf-wave-0p5-v2", "ecmwf_wave_waves_0p5", "waves"),
    (r"gfs-wave-0p5-v2", "gfs_wave_0p5", "waves"),
]


def api(path):
    """GET with manual paging (``per_page=100``) and a few retries (transient 5xx)."""
    import time
    out, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        for k in range(4):
            r = subprocess.run(["gh", "api", f"{path}{sep}page={page}"], capture_output=True,
                               text=True)
            if r.returncode == 0:
                break
            time.sleep(5 * (k + 1))
        else:
            raise RuntimeError(f"gh api {path}: {r.stderr[:200]}")
        got = json.loads(r.stdout)
        out += got
        if len(got) < 100:
            return out
        page += 1


rels = api(f"repos/{REPO}/releases?per_page=100")
assets = {r["tag_name"]: api(f"repos/{REPO}/releases/{r['id']}/assets?per_page=100") for r in rels}
done = {a["name"]: a["updated_at"] for a in assets.get("scores-v1", [])}
todo = []
for rx, pfx, kind in PRODUCTS:
    for tag, al in assets.items():
        if not re.fullmatch(rx, tag):
            continue
        last = {}
        for a in al:
            m = re.match(rf"{pfx}_(\d{{6}})(\d{{2}})?(_d\d+)?\.nc$", a["name"])
            if m:
                last[m.group(1)] = max(last.get(m.group(1), ""), a["updated_at"])
        for ym, t in last.items():
            if ym > os.environ.get("TRUTH_LAST", "202512"):  # no ERA5 truth in circeo-meteo yet
                continue
            s = done.get(f"scores_{pfx}_{ym}.nc")
            if s is None or s < t or s < os.environ.get("FORCE_BEFORE", ""):
                todo.append({"release": tag, "prefix": pfx, "kind": kind,
                             "year": int(ym[:4]), "month": int(ym[4:])})
# operational products (2023+) first, newest data first; the long reforecast last
todo.sort(key=lambda x: (x["prefix"].startswith("gefs_reforecast"), -x["year"], -x["month"],
                         x["prefix"]))
print(f"{len(todo)} (product, month) to score", file=sys.stderr)
print("matrix=" + json.dumps({"include": todo[:250]}) + "\nn=" + str(len(todo)))
