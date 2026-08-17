import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from streamlit.testing.v1 import AppTest

at = AppTest.from_file(str(Path(__file__).resolve().parent / "app.py"), default_timeout=90)
at.run()
print("exception count:", len(at.exception))
for exc in at.exception:
    print("EXC:", exc.value)
print("titles:", [t.value for t in at.title])
print("captions:", [c.value[:80] for c in at.caption][:3])

# simulate analyst login flow
at.text_input[0].set_value("admin@ffmitra.local")
at.text_input[1].set_value("Analyst@2026")
at.button[0].click().run()
print("after login exceptions:", len(at.exception))
print("markdown contains Command Center:", any("Command Center" in m.value for m in at.markdown))