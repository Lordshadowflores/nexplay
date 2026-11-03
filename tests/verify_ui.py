import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from streamlit.testing.v1 import AppTest
at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
def button(label): return next(b for b in at.button if b.label==label)
def submit():
    print('Submitting',flush=True)
    button('Buscar recomendaciones').click().run()
    assert not at.exception,at.exception
assert not at.exception
submit()
assert at.warning
for name in ['Fantasía e historia','Una tarde cozy','Acción sin costo','Fantasía e historia']:
    print(name,flush=True)
    button(name).click().run()
    submit()
    assert len(at.session_state.result_rows)==9
    assert at.session_state.answers['budget']=={'Fantasía e historia':30,'Una tarde cozy':10,'Acción sin costo':0}[name]
    if name=='Acción sin costo': assert all(r['price_usd']==0 for r in at.session_state.result_rows)
print('Profiles complete',flush=True)
old=[r['index'] for r in at.session_state.result_rows]
at.number_input(key='budget_value').set_value(0)
submit()
assert all(r['price_usd']==0 for r in at.session_state.result_rows)
next(b for b in at.button if b.key and b.key.startswith('fav_')).click().run()
assert len(at.session_state.favorites)==1
print('Library',flush=True)
at.sidebar.radio[0].set_value('Mi biblioteca').run()
at.sidebar.radio[0].set_value('Descubrir').run()
assert at.number_input(key='budget_value').value==0
assert at.multiselect(key='genres').value==['RPG','Adventure']
print('Reference mode',flush=True)
at.radio(key='mode').set_value('Un juego que me gusta').run()
assert at.session_state.answers is None
at.selectbox(key='reference_game').set_value(0).run()
submit()
at.radio(key='mode').set_value('Mis preferencias').run()
assert at.session_state.answers is None
button('Limpiar búsqueda').click().run()
assert not at.multiselect(key='genres').value
assert at.session_state.answers is None
assert len(at.session_state.favorites)==1
submit()
assert at.warning
assert not at.exception
print('PASS: repeated profiles, budget changes, mode changes, navigation persistence, reset and favorites')
