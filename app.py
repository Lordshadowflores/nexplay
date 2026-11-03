import logging
print("[NexPlay] Starting Python application", flush=True)
from pathlib import Path
import html
import json
import pandas as pd
import streamlit as st
from engine import Recommender
print("[NexPlay] Dependencies imported", flush=True)

ROOT=Path(__file__).parent
st.set_page_config(page_title='NexPlay · Tu próximo juego', page_icon='✦', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {--ink:#f1f2fa;--muted:#a0a7c0;--lime:#d7fa72;}
html, body, [class*="css"], .stApp {font-family:'DM Sans',sans-serif;}
.stApp{background:#0c0f18;color:var(--ink);}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:2.2rem;max-width:1440px;padding-bottom:3rem;}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.045em!important;}
h1{font-size:clamp(2.5rem,4vw,4.7rem)!important;line-height:1.04!important;font-weight:600!important;}
h2{font-size:1.65rem!important;} h3{font-size:1.1rem!important;}
[data-testid="stSidebar"]{background:#111522;border-right:1px solid #242a3c;}
[data-testid="stSidebar"] .block-container{padding-top:1.5rem;}
[data-testid="stForm"]{background:#121724;border:1px solid #293044;border-radius:20px;padding:24px;}
.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{border-radius:10px;min-height:42px;font-weight:600;}
button[kind="primary"], .stFormSubmitButton button{background:#d7fa72!important;border-color:#d7fa72!important;color:#11180a!important;}
.brand{font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700;letter-spacing:-1px;display:flex;gap:12px;align-items:center;}
.brandmark{display:inline-flex;background:#d7fa72;color:#141a0d;width:38px;height:38px;border-radius:11px;align-items:center;justify-content:center;font-size:25px;}
.tagline{font-size:10px;letter-spacing:2px;color:#8790aa;margin:10px 0 30px;}
.eyebrow{font-size:11px;letter-spacing:2px;color:#d7fa72;font-weight:700;margin:20px 0 15px;}
.intro{max-width:590px;font-size:16px;color:#aab2ca;line-height:1.7;margin:15px 0 28px;}
.hero-art{height:275px;border-radius:24px;border:1px solid #30384d;background:radial-gradient(ellipse at 60% 60%,#485a862f,transparent 65%),#121724;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;}
.orbit{position:absolute;width:215px;height:215px;border:1px solid #3e4965;border-radius:50%;transform:rotateX(55deg) rotate(-30deg);}
.orbit.two{transform:rotateX(35deg) rotate(55deg);width:245px;height:245px;}
.core{font-family:'Space Grotesk';font-size:76px;color:#d7fa72;z-index:2;text-shadow:0 0 55px #d7fa7255;}
.star{position:absolute;color:#d7fa72;font-size:25px;}
.art-label{position:absolute;bottom:18px;left:22px;font-size:10px;color:#929cb5;letter-spacing:2px;}
.statline{display:flex;gap:35px;margin-top:22px;color:#9fa8c0;font-size:12px;}
.statline strong{display:block;color:#edf0fb;font-family:'Space Grotesk';font-size:24px;margin-bottom:3px;}
.mini{font-size:11px;letter-spacing:1.8px;color:#939cb6;text-transform:uppercase;margin:18px 0 8px;}
.gamecard{border:1px solid #2a3246;border-radius:16px;background:#131927;overflow:hidden;margin-bottom:8px;}
.gameart{height:112px;position:relative;overflow:hidden;background:linear-gradient(125deg,var(--c1),#141a2d 70%);}
.gameart:before{content:'';position:absolute;width:140px;height:140px;border:28px solid #ffffff12;transform:rotate(35deg);right:-16px;top:-40px;border-radius:30px;}
.gameart:after{content:'';position:absolute;width:110px;height:110px;border:1px solid #ffffff30;transform:rotate(35deg);right:65px;top:35px;border-radius:20px;}
.rank{position:absolute;top:16px;left:18px;font-family:'Space Grotesk';font-size:27px;font-weight:600;color:#ffffffbb;}
.genre-art{position:absolute;bottom:14px;left:18px;color:#ffffffaa;font-size:10px;letter-spacing:2px;text-transform:uppercase;}
.gamebody{padding:18px;min-height:207px;}
.game-title{font-family:'Space Grotesk';font-size:19px;font-weight:600;color:#f3f4fc;line-height:1.25;min-height:48px;}
.game-meta{display:flex;justify-content:space-between;gap:10px;font-size:12px;color:#9da8c3;margin:10px 0 15px;}
.price{color:#d7fa72;font-weight:700;}
.chip{font-size:10px;color:#c6cce0;display:inline-block;border:1px solid #343d53;border-radius:20px;padding:3px 8px;margin:0 4px 5px 0;}
.match-label{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#8995b2;margin:8px 0 7px;}
.score{font-size:11px;color:#98a5c5;border-top:1px solid #283047;padding-top:11px;margin-top:8px;}
.empty{border:1px dashed #3c4661;border-radius:20px;padding:40px;text-align:center;color:#aab4ce;background:#121724;margin:18px 0;}
.footer{border-top:1px solid #273047;color:#7d89a6;font-size:11px;margin-top:45px;padding-top:20px;display:flex;justify-content:space-between;gap:20px;}
[data-testid="stMetric"]{background:#151b2a;border:1px solid #293249;border-radius:14px;padding:18px;}
@media(max-width:750px){.block-container{padding-top:1.5rem}.hero-art{height:180px}.intro{font-size:14px}.statline{gap:20px}.gamebody{min-height:175px}}
</style>''', unsafe_allow_html=True)

@st.cache_resource(show_spinner='Cargando tu modelo entrenado…')
def get_engine():
    print("[NexPlay] Loading catalog and encoder", flush=True)
    model = Recommender()
    print(f"[NexPlay] Model ready: {len(model.catalog)} records", flush=True)
    return model

try: engine=get_engine()
except Exception as exc:
    st.error('No se pudo cargar el modelo. Comprueba que la carpeta model esté completa y consulta la guía de instalación.')
    with st.expander('Detalle técnico'): st.code(str(exc))
    st.stop()

if 'favorites' not in st.session_state: st.session_state.favorites=[]
if 'answers' not in st.session_state: st.session_state.answers=None
if 'budget_value' not in st.session_state: st.session_state.budget_value=30.

PRESETS={
    'Fantasía e historia': {'genres':['RPG','Adventure'],'experience':['Un jugador'],'tags':['Fantasy','Story Rich'],'budget':30},
    'Una tarde cozy': {'genres':['Casual','Indie'],'experience':['Un jugador'],'tags':['Relaxing','Cute','2D'],'budget':10},
    'Acción sin costo': {'genres':['Action'],'experience':['Multijugador'],'tags':['Shooter'],'budget':0},
}
DEFAULTS={'genres':[], 'experience':[], 'selected_tags':[], 'budget_mode':'Definir máximo',
          'budget_value':30., 'quality':'Me da igual', 'strict':False, 'unknown':False,
          'age':'Sin filtro', 'avoid':[], 'needs':[], 'early':'Cualquiera',
          'unreleased':False, 'only_real':True, 'quantity':9, 'reference_game':None,
          'mode':'Mis preferencias', 'game_query':''}
# Retain widget values when switching to the library or model page.
for key,default in DEFAULTS.items():
    st.session_state[key]=st.session_state.get(key,default)

def clear_results():
    st.session_state.answers=None
    st.session_state.pop('result_rows',None)

def change_query():
    st.session_state.reference_game=None
    clear_results()

def new_search():
    for key,value in DEFAULTS.items(): st.session_state[key]=value.copy() if isinstance(value,list) else value
    clear_results()

def preset(name):
    new_search()
    p=PRESETS[name]
    st.session_state['genres']=p['genres']
    st.session_state['experience']=p['experience']
    st.session_state['selected_tags']=[t for t in p['tags'] if 'tag_'+t in engine.col]
    st.session_state['budget_value']=float(p['budget'])

def favorite(idx):
    f=st.session_state.favorites
    if idx in f: f.remove(idx)
    else: f.append(idx)

def export_table(rows):
    return pd.DataFrame([{'Juego':r['name'],'Géneros':r['genres'],'Precio USD':r['price_usd'] if r['price_known'] else None,
        'Similitud coseno':r.get('similarity'), 'Coincidencias':', '.join(r.get('matches',[])),
        'Steam':f"https://store.steampowered.com/app/{int(r['appid'])}/" if r['appid_real'] else ''} for r in rows])

def cards(rows, save=True):
    colors=['#3d426c','#285b59','#5c3c65','#594d2d','#2d526d','#3b5944']
    for offset in range(0,len(rows),3):
        cols=st.columns(3,gap='medium')
        for slot,row in enumerate(rows[offset:offset+3]):
            idx=int(row['index']); rank=offset+slot+1
            title=html.escape(str(row['name']))
            genres=html.escape(' · '.join(row['genres_list'][:2]))
            price='Sin precio registrado' if not row['price_known'] else ('Gratis' if row['price_usd']==0 else f"${row['price_usd']:.2f} USD")
            date=str(row['release_date'])[:4] or 'Fecha sin dato'
            tags=''.join(f'<span class="chip">{html.escape(t)}</span>' for t in row.get('matches',[])[:4])
            if not tags: tags='<span class="chip">Afinidad del embedding</span>'
            sim=row.get('similarity')
            sim_text=f'Similitud neuronal · {sim:.3f}' if sim is not None else 'Guardado en tu biblioteca'
            with cols[slot]:
                st.markdown(f'''<div class="gamecard"><div class="gameart" style="--c1:{colors[idx%len(colors)]}"><div class="rank">{rank:02d}</div><div class="genre-art">{genres}</div></div><div class="gamebody"><div class="game-title">{title}</div><div class="game-meta"><span>{html.escape(date)}</span><span class="price">{price}</span></div><div class="match-label">Coincide contigo</div>{tags}<div class="score">{sim_text}</div></div></div>''',unsafe_allow_html=True)
                a,b=st.columns([1.35,1])
                if row['appid_real']:
                    a.link_button('Ver en Steam ↗',f"https://store.steampowered.com/app/{int(row['appid'])}/",use_container_width=True)
                else: a.caption('Sin enlace verificado')
                b.button('♥ Guardado' if idx in st.session_state.favorites else '♡ Guardar',key=f'fav_{idx}',on_click=favorite,args=(idx,),use_container_width=True)

with st.sidebar:
    st.markdown('<div class="brand"><span class="brandmark">✦</span>NexPlay</div>',unsafe_allow_html=True)
    page=st.radio('Navegación',['Descubrir','Mi biblioteca','El modelo'],label_visibility='collapsed')
    st.divider()
    st.caption('1. Elige tus gustos o un juego de referencia.')
    st.caption('2. Ajusta el presupuesto.')
    st.caption('3. Pulsa Buscar recomendaciones.')
    st.caption('Puedes repetir la búsqueda cuantas veces quieras.')

if page=='Descubrir':
    st.title('Encuentra tu próximo juego')
    st.caption('Elige tus preferencias y descubre juegos con ayuda de tu red neuronal.')
    top=st.columns([3,1])
    top[0].caption('Empieza con un ejemplo o completa el formulario:')
    top[1].button('Limpiar búsqueda',on_click=new_search,use_container_width=True)
    for col,name in zip(st.columns(3),PRESETS): col.button(name,on_click=preset,args=(name,),use_container_width=True)
    mode=st.radio('¿Cómo quieres buscar?',['Mis preferencias','Un juego que me gusta'],horizontal=True,key='mode',on_change=clear_results)
    query=''
    if mode=='Un juego que me gusta':
        query=st.text_input('Busca un juego por nombre',key='game_query',on_change=change_query,placeholder='Por ejemplo: Stardew Valley')
        st.caption('Escribe parte del nombre. Se muestran hasta 100 coincidencias.')
    translations={'Action':'Acción','Adventure':'Aventura','Indie':'Independientes','Casual':'Casuales','Strategy':'Estrategia',
                  'Simulation':'Simulación','Sports':'Deportes','Racing':'Carreras','Massively Multiplayer':'Multijugador masivo'}
    labels={t:label for _,options in engine.options['GRUPOS_TAGS'].values() for label,t in options}
    with st.form('preferences'):
        reference=None
        if mode=='Mis preferencias':
            a,b=st.columns(2)
            offered=[g for g in ['Action','Adventure','Indie','Casual','RPG','Strategy','Simulation','Sports','Racing','Massively Multiplayer'] if g in engine.meta['top_genres']]
            genres=a.multiselect('¿Qué géneros te gustan?',offered,format_func=lambda g:translations.get(g,g),key='genres')
            experience=b.multiselect('¿Cómo te gusta jugar?',list(engine.options['EXPERIENCIAS']),key='experience')
            tags=st.multiselect('Temas y estilos (opcional)',[t for t in engine.all_tags if 'tag_'+t in engine.col],format_func=lambda t:labels.get(t,t),key='selected_tags',placeholder='Fantasía, relajante, mundo abierto…')
        else:
            reference_labels=[f'{name} · {int(appid)}' for name,appid in zip(engine.catalog['name'],engine.catalog['appid'])]
            reference=st.selectbox('Selecciona un juego del catálogo',[i for i in range(len(engine.catalog)) if engine.valid[i] and query.casefold() in str(engine.catalog.iloc[i]['name']).casefold()][:100],index=None,
                format_func=lambda i:reference_labels[i],key='reference_game',placeholder='Escribe el nombre del juego')
            genres=[];experience=[];tags=[]
        a,b,c=st.columns(3)
        budget_mode=a.selectbox('Presupuesto',['Definir máximo','Sin límite'],key='budget_mode')
        budget=b.number_input('Máximo por juego · USD',min_value=0.,max_value=500.,step=5.,key='budget_value')
        k=c.selectbox('Número de resultados',[6,9,12,15,18],key='quantity')
        st.caption('Escribe 0 para juegos gratuitos. Si eliges Sin límite, se ignora el importe.')
        with st.expander('Más filtros (opcional)'):
            a,b=st.columns(2)
            quality=a.selectbox('Preferencia por buenas reseñas',['Me da igual','Algo importante','Muy importante'],key='quality')
            strict=a.checkbox('Exigir al menos un género elegido',key='strict')
            unknown=a.checkbox('Incluir juegos sin precio',key='unknown')
            age_label=a.selectbox('Clasificación de edad',['Sin filtro','Hasta 13 años','Hasta 17 años','Hasta 18 años'],key='age')
            a.caption('Edad 0 puede significar falta de datos; no garantiza contenido apto para menores.')
            avoid_options={label:tags for label,tags in engine.options['EVITAR']}
            avoid=b.multiselect('Contenido a evitar',list(avoid_options),key='avoid')
            requirements={label:tags for label,tags in engine.options['REQUISITOS'] if any(t in engine.all_tags for t in tags)}
            needs=b.multiselect('Características obligatorias',list(requirements),key='needs')
            early_label=b.selectbox('Acceso anticipado',['Cualquiera','Excluir acceso anticipado','Solo acceso anticipado'],key='early')
            unreleased=b.checkbox('Incluir próximos lanzamientos',key='unreleased')
            only_real=b.checkbox('Solo juegos con enlace a Steam',key='only_real')
        submitted=st.form_submit_button('Buscar recomendaciones',use_container_width=True)
        if submitted:
            clear_results()
            if mode=='Mis preferencias' and not (genres or experience or tags): st.warning('Elige al menos un género, experiencia o tema.')
            elif mode=='Un juego que me gusta' and reference is None: st.warning('Selecciona un juego del catálogo.')
            else:
                answers={'genres':genres,'experience':experience,'tags':tags,
                    'review_target':{'Me da igual':None,'Algo importante':.8,'Muy importante':.95}[quality] if reference is None else None,
                    'strict_genres':strict,'budget':budget if budget_mode=='Definir máximo' else None,
                    'unknown_price':unknown,'age':{'Sin filtro':None,'Hasta 13 años':13,'Hasta 17 años':17,'Hasta 18 años':18}[age_label],
                    'exclude':[t for label in avoid for t in avoid_options[label]],'required':[requirements[n] for n in needs],
                    'early':{'Cualquiera':None,'Excluir acceso anticipado':'no','Solo acceso anticipado':'only'}[early_label],
                    'unreleased':unreleased,'only_real':only_real}
                with st.spinner('Buscando juegos…'):
                    rows,count=engine.recommend(answers,reference=reference,k=k)
                st.session_state.answers=answers
                st.session_state.result_rows=rows
                st.session_state.result_count=count
                st.session_state.reference=reference
                st.session_state.result_mode=mode
    if 'result_rows' in st.session_state:
        rows=st.session_state.result_rows
        st.subheader('Tus recomendaciones')
        st.caption(f"{len(rows)} resultados · {st.session_state.result_count:,} juegos compatibles con la última búsqueda")
        st.info('Para otra recomendación, cambia las opciones de arriba y pulsa Buscar recomendaciones. Los resultados permanecen hasta que envíes una nueva búsqueda.')
        if rows:
            st.download_button('Descargar resultados',export_table(rows).to_csv(index=False).encode('utf-8-sig'),'nexplay_recomendaciones.csv','text/csv')
            cards(rows)
        else: st.warning('Ningún juego cumple estos filtros. Amplía el presupuesto o reduce los requisitos y vuelve a buscar.')
    else: st.caption('Completa el formulario y pulsa Buscar recomendaciones para ver tus juegos.')

elif page=='Mi biblioteca':
    st.markdown('<div class="eyebrow">TUS DESCUBRIMIENTOS</div>',unsafe_allow_html=True)
    st.title('Guarda la próxima partida.')
    st.caption('Tu selección se mantiene durante esta sesión. Descárgala antes de cerrar la aplicación.')
    rows=[]
    for i in st.session_state.favorites:
        r=engine.catalog.iloc[i].to_dict();r.update(index=i,genres_list=engine.genres[i],matches=[]);rows.append(r)
    if rows:
        st.download_button('↓ Descargar mi biblioteca',export_table(rows).to_csv(index=False).encode('utf-8-sig'),'nexplay_biblioteca.csv','text/csv')
        cards(rows)
    else: st.info('Aún no has guardado juegos. Explora las recomendaciones y pulsa ♡ Guardar.')

else:
    st.markdown('<div class="eyebrow">DE LOS DATOS A TU PRÓXIMO JUEGO</div>',unsafe_allow_html=True)
    st.title('Una red que aprende conexiones.')
    st.write('Un autoencoder aprende a reconstruir los atributos de cada videojuego. Su capa central comprime esa información en un embedding de 32 dimensiones: juegos similares tienden a quedar cerca.')
    a,b,c,d=st.columns(4)
    a.metric('Características de entrada',len(engine.columns));b.metric('Dimensiones del embedding',engine.embeddings.shape[1]);c.metric('MSE de prueba · notebook','0.02582');d.metric('Mejora · notebook','61.4 %')
    st.caption('Métricas de la ejecución guardada en el notebook, no una evaluación de los pesos actuales. El ZIP muestra similitudes diferentes y pudo generarse en otra ejecución. Estas métricas no miden satisfacción de usuarios.')
    st.markdown('## Cómo se genera una recomendación')
    st.code('Preferencias → Vector de 234 atributos → Encoder 128 → 64 → 32\n                                                      ↓\n+Filtros obligatorios ← Ranking ← Coseno con embeddings del catálogo'.replace('+Filtros','Filtros'),language=None)
    st.write('Las preferencias sin respuesta conservan el valor medio de entrenamiento. El perfil pasa por los pesos reales del encoder. Después se calcula su similitud coseno con los embeddings exportados y se aplican los filtros. En la búsqueda por juego se utiliza directamente su embedding.')
    st.markdown('## Registro de entrenamiento del notebook')
    train=json.loads((ROOT/'assets'/'entrenamiento.json').read_text(encoding='utf-8'))
    if train:
        df=pd.DataFrame(train).set_index('epoca')[['loss','val_loss']].rename(columns={'loss':'Entrenamiento','val_loss':'Validación'})
        st.line_chart(df,color=['#d7fa72','#8e9dff'],x_label='Época',y_label='MSE')
        st.caption('Curvas reconstruidas a partir de las 98 épocas guardadas en el notebook. El registro muestra restauración de pesos de la época 88; el menor val_loss registrado corresponde a la época 97.')
    if (ROOT/'assets'/'evaluacion_original.png').exists():
        with st.expander('Ver figura original de evaluación'): st.image(str(ROOT/'assets'/'evaluacion_original.png'),width='stretch')
    st.dataframe(pd.DataFrame({'Conjunto':['Entrenamiento','Validación','Prueba'],'MSE':[.02511,.02565,.02582],'MAE':[.07413,.07477,.07473],'Reducción frente a línea base':['62.7 %','61.9 %','61.4 %']}),hide_index=True,width='stretch')
    with st.expander('Alcance de esta entrega y datos disponibles',expanded=True):
        st.write('Esta versión usa el ranking neuronal por coseno. El ZIP original no incluye la matriz de características del catálogo, la matriz TF-IDF ni los campos de plataforma e idiomas. Por ello, no reproduce la mezcla de puntajes de la celda 8 ni ofrece esos filtros. Se incluye exportar_completo_colab.py para conservar esos datos en una futura ampliación.')
        st.write('El precio se muestra en USD tal como fue exportado. Los registros con price_known = 0 tienen precio desconocido. La edad 0 es ambigua y no garantiza contenido apto para menores. Las etiquetas y reseñas reflejan el dataset, no consultas en tiempo real.')
        st.write('La inferencia ejecuta las operaciones Dense y ReLU con NumPy y lee los pesos Keras originales. Dropout está desactivado durante inferencia. No requiere GPU ni reentrenamiento.')
    with open(ROOT/'PIA_Redes_Neuronales.ipynb','rb') as f: st.download_button('↓ Descargar notebook original',f.read(),'PIA_Redes_Neuronales.ipynb')

st.markdown('<div class="footer"><span>✦ NexPlay · Recomendación de videojuegos con redes neuronales</span><span>PIA · Autoencoder no supervisado</span></div>',unsafe_allow_html=True)
