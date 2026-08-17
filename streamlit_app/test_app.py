import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from streamlit.testing.v1 import AppTest

at = AppTest.from_file(str(Path(__file__).resolve().parent / "app.py"), default_timeout=120)
at.run()
print("exception count:", len(at.exception))
for exc in at.exception:
    print("EXC:", exc.value)
print("titles:", [t.value for t in at.title])
print("captions:", [c.value[:80] for c in at.caption][:3])

# simulate analyst login flow (find buttons by label — victim page also has buttons)
sign_in = [b for b in at.button if b.label == "Sign in"]
assert sign_in, "Sign in button not found"
at.text_input[0].set_value("admin@ffmitra.local")
at.text_input[1].set_value("Analyst@2026")
sign_in[0].click().run()
print("after login exceptions:", len(at.exception))
for exc in at.exception:
    print("EXC:", exc.value)
print("markdown contains Command Center:", any("Command Center" in m.value for m in at.markdown))

# navigate to Command Center (all tab blocks execute regardless of selection,
# so exceptions inside any tab surface right here)
at.radio[0].set_value([o for o in at.radio[0].options if "Command Center" in o][0]).run()
print("tabs:", [t.label for t in at.tabs])
assert at.tabs, "Command Center tabs not rendered (login failed?)"
print("command center exceptions:", len(at.exception))
for exc in at.exception:
    print("EXC:", exc.value)

# simulate a link analysis (Link Analyzer block already executed)
url_box = next(t for t in at.text_input if t.label == "Suspicious URL")
url_box.set_value("http://hdfc-bank-login.xyz/verify")
analyze = [b for b in at.button if b.label == "Analyze link"]
assert analyze, "Analyze link button not found"
analyze[0].click().run()
print("after analyze exceptions:", len(at.exception))
for exc in at.exception:
    print("EXC:", exc.value)
print("risk markdown:", any("Risk score" in m.value for m in at.markdown))

# simulate a fund-trail trace (seed defaults to mule.vendor@paytm)
trace = [b for b in at.button if b.label == "Trace"]
assert trace, "Trace button not found"
trace[0].click().run()
print("after trace exceptions:", len(at.exception))
for exc in at.exception:
    print("EXC:", exc.value)
print("trail markdown:", any("accounts" in m.value and "transfers" in m.value for m in at.markdown))
print("graphviz charts:", len(at.get("graphviz_chart")))

# CSV downloads must exist on dashboard (rendered outside the auto-refresh fragment)
dls = at.get("download_button")
print("download buttons:", [d.label for d in dls])
assert any("Summary report" in d.label for d in dls), "summary CSV download missing"
assert any("Blocked transactions" in d.label for d in dls), "blocked CSV download missing"
assert any("Review queue" in d.label for d in dls), "review CSV download missing"
print("csv payloads attached:", all(getattr(d, "url", "") for d in dls))

# admin tab: create a throwaway analyst (requires the real admin password),
# verify success, then remove it via the UI — cleanup keeps auth clean
TEST_ANALYST = "apptest-e2e@ffmitra.local"

# ensure a clean slate: drop any leftover from a previous failed run
import httpx

from app.config import get_settings as _gs

_s = _gs()
_h = {"apikey": _s.supabase_secret_key, "Authorization": f"Bearer {_s.supabase_secret_key}"}
_leftover = httpx.get(
    f"{_s.supabase_url.rstrip('/')}/auth/v1/admin/users?per_page=100", headers=_h, timeout=30
).json().get("users", [])
for u in _leftover:
    if u.get("email") == TEST_ANALYST:
        httpx.delete(f"{_s.supabase_url.rstrip('/')}/auth/v1/admin/users/{u['id']}", headers=_h, timeout=30)

for t in at.text_input:
    if t.label == "New analyst email":
        t.set_value(TEST_ANALYST)
    elif t.label == "Temporary password":
        t.set_value("Temp@12345")
    elif t.label == "Your admin password (authorization)":
        t.set_value("Analyst@2026")
create_btn = [b for b in at.button if b.label == "Create analyst"]
assert create_btn, "Create analyst button not found"
create_btn[0].click().run()
print("after create analyst exceptions:", len(at.exception))
for exc in at.exception:
    print("EXC:", exc.value)
print("created analyst success:", any("created" in s.value.lower() for s in at.success))

# reset the throwaway analyst's password via the UI, then verify login works
reset_sel = next(x for x in at.selectbox if x.label == "Analyst to reset")
reset_sel.set_value(TEST_ANALYST)
next(x for x in at.text_input if x.label == "New temporary password").set_value("Temp@67890")
next(x for x in at.text_input if x.label == "Your admin password (to reset)").set_value("Analyst@2026")
[x for x in at.button if x.label == "Reset password"][0].click().run()
print("after reset exceptions:", len(at.exception))
print("reset success:", any("reset" in s.value.lower() for s in at.success))

# verify the new password actually signs in (Supabase is the source of truth)
from app import db as _db  # noqa: F401  (ensure backend on path)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import httpx as _httpx

_resp = _httpx.post(
    f"{_s.supabase_url.rstrip('/')}/auth/v1/token?grant_type=password",
    headers={"apikey": _s.supabase_publishable_key or _s.supabase_secret_key, "Content-Type": "application/json"},
    json={"email": TEST_ANALYST, "password": "Temp@67890"},
    timeout=30,
)
print("new password login status:", _resp.status_code)

# remove the analyst via the UI (password-gated), then verify it's gone
sel = next(s for s in at.selectbox if s.label == "Analyst to remove")
sel.set_value(TEST_ANALYST)
confirm_chk = next(c for c in at.checkbox if "permanently removes" in c.label)
confirm_chk.check()
rm_pw = next(t for t in at.text_input if t.label == "Your admin password (to remove)")
rm_pw.set_value("Analyst@2026")
rm_btn = [b for b in at.button if b.label == "🗑 Remove analyst"]
assert rm_btn, "Remove analyst button not found"
rm_btn[0].click().run()
print("after remove exceptions:", len(at.exception))
for exc in at.exception:
    print("EXC:", exc.value)
print("removed success:", any("removed" in s.value.lower() for s in at.success))

# verify against Supabase directly (source of truth)
_users = httpx.get(
    f"{_s.supabase_url.rstrip('/')}/auth/v1/admin/users?per_page=100", headers=_h, timeout=30
).json().get("users", [])
print("gone from supabase:", not any(u.get("email") == TEST_ANALYST for u in _users))

# cleanup: delete the throwaway user via the admin API as belt-and-braces
for u in _users:
    if u.get("email") == TEST_ANALYST:
        resp = httpx.delete(
            f"{_s.supabase_url.rstrip('/')}/auth/v1/admin/users/{u['id']}",
            headers=_h,
            timeout=30,
        )
        print("cleanup delete:", resp.status_code)