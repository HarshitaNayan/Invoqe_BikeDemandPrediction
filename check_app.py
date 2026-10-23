"""Developer smoke check for page rendering and the actual prediction form."""
from pathlib import Path
from streamlit.testing.v1 import AppTest
app=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=60).run()
assert not app.exception, app.exception
app.button[0].click().run()
assert not app.exception, app.exception
assert app.session_state['last_prediction']['value'] >= 0
assert any('rentals in one hour.' in item.value for item in app.markdown)
print('PASS: all tabs render and submitting the form produces a prediction')
