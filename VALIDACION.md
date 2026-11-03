# Validación de la entrega

Comprobaciones realizadas con Python 3.12 y las versiones de `requirements.txt`.

| Comprobación | Resultado |
|---|---|
| Carga del catálogo y embeddings | 22,747 filas, 32 dimensiones; appid únicos |
| Entrada del encoder | 234 atributos, capas 128 / 64 / 32 |
| Inferencia frente a Keras | Error absoluto máximo **0.0** en los tres perfiles comprobados: neutro, RPG/fantasía y acción gratuita |
| Pruebas automatizadas del motor | **6 aprobadas** |
| Pruebas de flujos con Streamlit AppTest | Inicio, formulario vacío, perfil de ejemplo, resultados, favoritos, biblioteca, métricas y búsqueda por juego aprobados |
| Revisión en navegador | Perfil de fantasía genera nueve recomendaciones reales con enlaces y similitudes |
| Salud del servidor local | HTTP 200 en `/_stcore/health` |

Las pruebas del motor comprueban dimensiones y alineación por filas, filtros de presupuesto/gratuidad, edad, géneros obligatorios, contenido excluido, características requeridas, orden determinista, exclusión del juego de origen y ausencia de resultados cuando ningún juego cumple las restricciones.

La comparación con Keras se hizo cargando directamente el encoder original con backend NumPy. Keras y JAX fueron dependencias de verificación, no son necesarias para ejecutar la aplicación entregada. Los tres perfiles produjeron los mismos vectores con el motor de inferencia incluido.

La revisión visual incluye la página de inicio y las tarjetas de resultados a 1280 × 720. Las capturas están en `assets/interfaz_inicio.jpg` y `assets/interfaz_resultados.jpg`. No se realizó una comprobación visual exhaustiva en teléfonos.

## Diferencia entre el ZIP y el notebook

Para Counter-Strike 2, el primer vecino del ZIP es World of Tanks Blitz con coseno **0.934449**. El notebook guardado también presenta ese primer vecino, con coseno **0.874**. Por ello las métricas de entrenamiento se identifican como históricas del notebook, sin afirmar que correspondan a los pesos del ZIP. La aplicación usa exclusivamente los pesos y embeddings actuales recibidos.

Estas comprobaciones verifican funcionamiento y consistencia de inferencia. No constituyen una nueva evaluación del autoencoder ni un estudio de satisfacción de usuarios.

## Revisión de búsquedas consecutivas

Se unificaron las opciones en un solo formulario y se guardan los resultados de la última búsqueda enviada. Cambiar de modo o limpiar descarta los resultados anteriores. Las opciones se conservan al visitar la biblioteca. Los ejemplos restablecen todos los filtros para evitar combinaciones heredadas.

La prueba tests/verify_ui.py cubre cuatro perfiles consecutivos, cambio de presupuesto a cero, cambio de modo, navegación, limpieza y conservación de favoritos. Las capturas anteriores corresponden al diseño inicial.
