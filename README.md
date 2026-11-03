# NexPlay — entrega final

Aplicación en español para recomendar videojuegos con el encoder entrenado del proyecto PIA Redes Neuronales. Incluye interfaz, pesos originales, catálogo, notebook y evidencia de evaluación.

## Ejecutar en Windows

1. Extrae la carpeta completa; no ejecutes archivos dentro del ZIP.
2. Instala **Python 3.12** desde https://www.python.org/downloads/ si aún no lo tienes.
3. Abre `INICIAR_WINDOWS.bat`. La primera ejecución instala las dependencias en `.venv` y requiere Internet.
4. Abre http://localhost:8501 si el navegador no se abre automáticamente.
5. Mantén abierta la ventana del servidor. Para detenerlo pulsa Ctrl+C.

También puedes usar una terminal en esta carpeta:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py --server.address localhost
```

En macOS/Linux con Python 3.12:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address localhost
```

La inferencia es local y funciona sin GPU, sin conexión a Colab y sin entrenar nuevamente. Los enlaces a Steam y la fuente web opcional necesitan Internet. Las fuentes del sistema se usan cuando la fuente web no está disponible.

## Funciones incluidas

- Cuestionario con géneros, modalidad de juego, etiquetas y categorías en español.
- Perfiles de ejemplo: fantasía, cozy y acción gratuita.
- Búsqueda de juegos similares a un videojuego del catálogo.
- Filtros obligatorios de presupuesto, edad registrada, contenido a evitar, características, acceso anticipado y lanzamiento.
- Tarjetas con precio del catálogo, motivos de coincidencia y similitud neuronal.
- Enlaces a Steam solo para registros con `appid_real = 1`.
- Biblioteca de favoritos durante la sesión y exportación CSV.
- Página del modelo con arquitectura, curvas de 98 épocas y métricas reales del notebook.

Las preferencias del formulario se aplican al pulsar **Buscar recomendaciones**. Todos los filtros se aplican juntos al enviar el formulario. Limpiar búsqueda restablece las opciones y conserva los favoritos. Los favoritos no se guardan entre sesiones: descarga tu biblioteca para conservarla.

## Guion sugerido para la presentación

1. Explica el problema: descubrir videojuegos en un catálogo amplio.
2. Elige **Fantasía e historia**, revisa el formulario y genera resultados.
3. Cambia el presupuesto para mostrar que los filtros son obligatorios.
4. Guarda un juego y muestra **Mi biblioteca**, con descarga CSV.
5. Cambia a **Un juego que me gusta** y busca `The Witcher 3` o `Stardew Valley`.
6. Abre **El modelo** y explica el autoencoder y el error de reconstrucción.

El MSE es error de reconstrucción de atributos, no precisión de recomendaciones. La mejora de 61.4 % es frente a predecir el vector medio en prueba, no porcentaje de usuarios satisfechos.

## Modelo y funcionamiento

El encoder real tiene arquitectura `234 → 128 ReLU → Dropout → 64 ReLU → 32 lineal`. Se cargan las matrices de los archivos `.keras` mediante HDF5 y se ejecuta la inferencia Dense/ReLU con NumPy. Dropout se omite como corresponde a inferencia. No se crean pesos nuevos. Los 22,747 embeddings se leen del archivo original `embeddings_catalogo.npy`.

Para el cuestionario se parte del perfil neutro de entrenamiento y se modifican las columnas seleccionadas. Los valores numéricos se transforman con los parámetros del MinMaxScaler exportado. Se compara el embedding del perfil contra los embeddings del catálogo mediante similitud coseno. Para vecinos de un juego se usa su embedding directamente. Finalmente se descartan los registros que incumplen las restricciones y se ordena por similitud.

El preprocesamiento se extrajo una vez del pickle original con scikit-learn 1.6.1 a `model/preprocesamiento.json`. La app no ejecuta ni deserializa el pickle, y no requiere TensorFlow ni scikit-learn. Se conserva el pickle original para trazabilidad.

## Alcance y limitaciones verificadas

El ZIP recibido exporta un catálogo reducido. No contiene `game_vectors`, la matriz de búsqueda TF-IDF, las descripciones, las plataformas ni los idiomas. Por eso:

- Esta entrega implementa **ranking neuronal por coseno**, sin la mezcla de similitud de columnas/embedding/TF-IDF del notebook. Sus resultados pueden diferir del cuestionario original.
- No se ofrecen filtros de plataforma o idiomas ni búsqueda semántica libre por descripción, porque no pueden verificarse con estos artefactos.
- Los géneros son preferencias; la opción **Exigir al menos un género elegido** los convierte en restricción.
- Las reseñas son una preferencia sobre el perfil y no un umbral obligatorio. El catálogo reducido no distingue un valor neutro 0.5 de una reseña real de 50 %; la interfaz evita presentar un porcentaje de reseñas por juego.
- Los precios están en USD y son una fotografía del dataset. Un precio imputado no se muestra como real cuando `price_known = 0`. Para presupuesto cero se admiten únicamente precios conocidos iguales a cero.
- Edad 0 significa sin restricción registrada o sin dato, y pasa el filtro de edad igual que en el notebook. No certifica contenido apto para menores.
- Los filtros dependen de las etiquetas y atributos del catálogo; no son una certificación de seguridad de contenido.
- Las métricas y curvas se extrajeron de las salidas guardadas del notebook. **No evalúan los pesos actuales del ZIP**: las similitudes guardadas difieren de las del ZIP recibido (por ejemplo Counter-Strike 2 → World of Tanks Blitz: 0.874 en el notebook frente a 0.934449 en el ZIP), lo que sugiere otra ejecución. No se ha reentrenado ni revaluado el conjunto de prueba. El registro del notebook restaura la época 88 aunque el mínimo exacto de validación aparece en la 97 por el `min_delta` de EarlyStopping.
- Las cabeceras de las tarjetas son ilustraciones geométricas, no portadas oficiales.

`exportar_completo_colab.py` incluye una celda opcional para exportar todas las matrices y campos desde la sesión original sin reentrenar. Es material para ampliar el motor después; el ZIP ampliado no se integra automáticamente en esta versión.

## Archivos

| Archivo | Función |
|---|---|
| `app.py` | Interfaz Streamlit |
| `engine.py` | Carga del encoder, perfil, filtros y ranking |
| `model/` | Modelos originales, embeddings, catálogo y metadatos |
| `assets/` | Curvas y figura original del notebook |
| `PIA_Redes_Neuronales.ipynb` | Notebook de origen sin modificar |
| `exportar_completo_colab.py` | Exportación ampliada opcional |
| `tests/test_engine.py` | Pruebas del ranking y restricciones |
| `VALIDACION.md` | Evidencia de comprobaciones realizadas |

Para volver a ejecutar las pruebas del motor, desde esta carpeta:

```sh
python -m unittest discover -s tests -v
```

Fuentes de referencia: [Streamlit](https://docs.streamlit.io/get-started), [formato de guardado de Keras](https://keras.io/guides/serialization_and_saving/). El trabajo y los resultados del proyecto proceden del notebook y los artefactos proporcionados.

