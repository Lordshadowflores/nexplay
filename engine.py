"""Inference using the exported dense encoder and its actual trained weights.

No training, random recommendations, or TensorFlow runtime is required.
The basic export supports neural cosine ranking, not the notebook's full hybrid.
"""
import io
import json
import re
import zipfile
from pathlib import Path
import h5py
import numpy as np
import pandas as pd

SOFTWARE = {'Utilities','Design & Illustration','Animation & Modeling','Video Production',
            'Game Development','Education','Audio Production','Photo Editing',
            'Software Training','Web Publishing','Accounting'}

def normalize(x):
    x = np.asarray(x, dtype=np.float32)
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-8)

def split(value):
    return [s.strip() for s in str(value).split(',') if s.strip()]

class Recommender:
    def __init__(self, directory=None):
        self.root = Path(directory or Path(__file__).parent / 'model')
        self.meta = json.loads((self.root/'preprocesamiento.json').read_text(encoding='utf-8'))
        self.options = json.loads((self.root/'opciones.json').read_text(encoding='utf-8'))
        self.catalog = pd.read_parquet(self.root/'catalogo.parquet').reset_index(drop=True)
        self.embeddings = np.load(self.root/'embeddings_catalogo.npy', allow_pickle=False)
        self.columns = self.meta['GAME_FEATURE_COLUMNS']
        self.col = {c:i for i,c in enumerate(self.columns)}
        self.numeric = {c:i for i,c in enumerate(self.meta['numeric_cols'])}
        self.neutral = np.array(self.meta['perfil_neutro'], dtype=np.float32)
        self.layers = []
        with zipfile.ZipFile(self.root/'nexplat_encoder.keras') as z:
            config = json.loads(z.read('config.json'))['config']['layers']
            with h5py.File(io.BytesIO(z.read('model.weights.h5')), 'r') as f:
                groups = {}
                for key, group in f['layers'].items():
                    v = group.get('vars')
                    if v is not None and '0' in v and '1' in v:
                        name = v.attrs.get('name', key)
                        if isinstance(name, bytes): name=name.decode()
                        groups[name] = (v['0'][:], v['1'][:])
                dense_count = 0
                for layer in config:
                    cls = layer['class_name']
                    if cls == 'Dense':
                        spec = layer['config']
                        key = 'dense' if dense_count == 0 else f'dense_{dense_count}'
                        group = groups.get(spec['name'])
                        if group is None:
                            v = f['layers'][key]['vars']
                            group = (v['0'][:], v['1'][:])
                        if spec['activation'] not in ('relu','linear'): raise ValueError('Unsupported encoder activation')
                        self.layers.append((*group, spec['activation']))
                        dense_count += 1
                    elif cls not in ('InputLayer','Dropout'):
                        raise ValueError(f'Unsupported encoder layer: {cls}')
        if self.embeddings.shape != (len(self.catalog), self.layers[-1][1].size):
            raise ValueError('Catalog and embeddings are not aligned')
        if self.layers[0][0].shape[0] != len(self.columns): raise ValueError('Feature dimensions differ')
        if not np.isfinite(self.embeddings).all(): raise ValueError('Nonfinite catalog embeddings')
        self.normalized = normalize(self.embeddings)
        self.genres = self.catalog['genres'].map(split).tolist()
        self.tags = self.catalog['tags'].map(split).tolist()
        self.all_tags = sorted({t for row in self.tags for t in row})
        self.dates = pd.to_datetime(self.catalog['release_date'], errors='coerce')
        self.valid = np.array([not any(g in SOFTWARE for g in row) for row in self.genres])

    def encode(self, vectors):
        x = np.atleast_2d(vectors).astype(np.float32)
        for w,b,activation in self.layers:
            x=x@w+b
            if activation=='relu': x=np.maximum(x,0)
        return x

    def set_numeric(self, vector, name, value):
        if name not in self.numeric: return
        i = self.numeric[name]
        vector[self.col[name]] = np.clip(value*self.meta['scale'][i]+self.meta['offset'][i],0,1)

    def profile(self, answers):
        v=self.neutral.copy()
        if answers.get('genres'):
            offered = [g for g in self.meta['top_genres'] if g not in SOFTWARE]
            for g in offered: v[self.col['genre_'+g]]=float(g in answers['genres'])
        if answers.get('experience'):
            chosen={t for e in answers['experience'] for t in self.options['EXPERIENCIAS'][e]}
            for t in {t for ts in self.options['EXPERIENCIAS'].values() for t in ts}:
                if 'tag_'+t in self.col: v[self.col['tag_'+t]]=float(t in chosen)
        for t in answers.get('tags',[]):
            if 'tag_'+t in self.col: v[self.col['tag_'+t]]=1
        if answers.get('budget') is not None:
            for c in ['price_log','initialprice_log']: self.set_numeric(v,c,np.log1p(answers['budget']*.5))
            self.set_numeric(v,'price_known',1)
            if answers['budget']==0: self.set_numeric(v,'is_free',1)
        if answers.get('review_target'):
            self.set_numeric(v,'review_score',answers['review_target'])
            self.set_numeric(v,'review_known',1)
        return v

    def mask(self, answers):
        df=self.catalog
        ok=self.valid.copy()
        if not answers.get('unreleased',False): ok &= ~(self.dates > pd.Timestamp.now().normalize()).to_numpy()
        known=df['price_known'].to_numpy()==1
        price=df['price_usd'].to_numpy()
        budget=answers.get('budget')
        if budget is not None:
            ok &= (known & (price<=budget)) | (~known & bool(answers.get('unknown_price',False)) & (budget>0))
        elif not answers.get('unknown_price',False): ok &= known
        if answers.get('age') is not None: ok &= df['required_age'].to_numpy()<=answers['age']
        if answers.get('only_real',False): ok &= df['appid_real'].to_numpy()==1
        if answers.get('strict_genres') and answers.get('genres'):
            chosen=set(answers['genres'])
            ok &= np.array([bool(chosen.intersection(gs)) for gs in self.genres])
        required=answers.get('required',[])
        for group in required: ok &= np.array([bool(set(group).intersection(ts)) for ts in self.tags])
        excluded=set(answers.get('exclude',[]))
        if excluded: ok &= np.array([not bool(excluded.intersection(ts)) for ts in self.tags])
        if answers.get('early')=='no': ok &= np.array(['Early Access' not in (g+t) for g,t in zip(self.genres,self.tags)])
        if answers.get('early')=='only': ok &= np.array(['Early Access' in (g+t) for g,t in zip(self.genres,self.tags)])
        if answers.get('min_reviews') is not None: ok &= df['review_score'].to_numpy() >= answers['min_reviews']
        return ok

    def recommend(self, answers, reference=None, k=9):
        embedding = self.embeddings[reference] if reference is not None else self.encode(self.profile(answers))[0]
        scores=(self.normalized@normalize(embedding)).astype(float)
        eligible=self.mask(answers)
        if reference is not None: eligible[reference]=False
        scores[~eligible]=-np.inf
        indices=np.flatnonzero(eligible)
        indices=indices[np.argsort(-scores[indices],kind='stable')[:k]]
        wanted=set(answers.get('tags',[]))
        for e in answers.get('experience',[]): wanted.update(self.options['EXPERIENCIAS'][e])
        wanted_genres=set(answers.get('genres',[]))
        if reference is not None:
            wanted.update(self.tags[reference]); wanted_genres.update(self.genres[reference])
        rows=[]
        for i in indices:
            row=self.catalog.iloc[i].to_dict()
            row.update(index=int(i), similarity=float(scores[i]), genres_list=self.genres[i],
                       matches=sorted(wanted_genres.intersection(self.genres[i]))+sorted(wanted.intersection(self.tags[i])))
            rows.append(row)
        return rows,int(eligible.sum())
