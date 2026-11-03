"""Pegar en una celda de Colab después de ejecutar las secciones 1 a 8.
Conserva el material necesario para reproducir después el ranking híbrido.
No ejecuta un nuevo entrenamiento. Este ZIP ampliado no se instala automáticamente.
"""
from pathlib import Path
import json
import pickle
import shutil
import numpy as np
from scipy.sparse import save_npz
from google.colab import files

needed=['df_model','game_vectors','encoder','autoencoder','emb_all','matriz_busqueda','scaler_games',
        'numeric_cols','GAME_FEATURE_COLUMNS','top_genres','top_tags','perfil_neutro','PESO_RED','PESO_TEXTO',
        'PESO_NUMERICAS','tfidf_busqueda','canon_tag','history']
missing=[name for name in needed if name not in globals()]
if missing: raise RuntimeError('Primero ejecuta las secciones 1 a 8. Faltan: '+', '.join(missing))
dest=Path('/content/nexplay_completo')
dest.mkdir(exist_ok=True)
encoder.save(dest/'nexplat_encoder.keras')
autoencoder.save(dest/'nexplat_autoencoder.keras')
np.save(dest/'game_vectors.npy',game_vectors)
np.save(dest/'embeddings_catalogo.npy',emb_all)
df_model.to_parquet(dest/'catalogo_completo.parquet',index=False)
save_npz(dest/'matriz_busqueda.npz',matriz_busqueda)
with (dest/'artefactos.pkl').open('wb') as f:
    pickle.dump({name:globals()[name] for name in needed if name in ['scaler_games','numeric_cols','GAME_FEATURE_COLUMNS',
        'top_genres','top_tags','perfil_neutro','PESO_RED','PESO_TEXTO','PESO_NUMERICAS','tfidf_busqueda','canon_tag']},f)
(dest/'historial.json').write_text(json.dumps({k:[float(v) for v in vs] for k,vs in history.history.items()}))
archive=shutil.make_archive(str(dest),'zip',dest)
files.download(archive)
