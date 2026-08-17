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