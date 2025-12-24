# visionArtificial

## Descripción 🔧

Repositorio con el laboratorio de **Mejora de Imagen — Operaciones Elementales**, orientado a analizar y mejorar imágenes con baja iluminación (Dataset: *The Dark Face*). El script principal `mejoraImagenes.py` implementa la clase `ImageEnhancer` que aplica múltiples técnicas de mejora, calcula métricas cuantitativas y genera reportes y gráficos listos para informes académicos.

## Características ✅

- Técnicas implementadas: **Negativo**, **Transformación logarítmica**, **Corrección Gamma**, **Estiramiento lineal**, **Ecualización**, **CLAHE**, **Multiplicación por escalar**, **Promediado**.
- Métricas calculadas: **Media**, **Desviación estándar**, **Mínimo/Máximo**, **Rango dinámico**, **Contraste (RMS)**, **Entropía**, **Δ Entropía**, **PSNR**, **SSIM**, **Coef. de variación**, **Kurtosis**, **Skewness**, **Nitidez (bordes)**.
- Salidas: tablas en **CSV / Excel / LaTeX**, gráficos comparativos en **PNG**, resúmenes estadísticos por categoría y recomendaciones automáticas por imagen.
- Interfaz: modo interactivo desde `mejoraImagenes.py` y uso programático importando `ImageEnhancer`.

## Requisitos ⚠️

- Python 3.8+
- Dependencias (instalables vía pip):
  - numpy, matplotlib, pillow, opencv-python, pandas, seaborn, scipy, xlsxwriter
  - `kagglehub` (opcional, sólo si desea descargar el dataset desde Kaggle automáticamente)

Ejemplo de instalación rápida:

```bash
pip install numpy matplotlib pillow opencv-python pandas seaborn scipy xlsxwriter
# kagglehub es opcional
pip install kagglehub
```

## Uso 📋

### Modo interactivo (CLI)

Ejecute el script principal:

```bash
python mejoraImagenes.py
```

Se mostrará un menú con opciones:
1. Descargar dataset Dark Face (requiere `kagglehub`)
2. Usar una ruta local de imágenes
3. Crear/usar una imagen de prueba

El procesamiento genera una carpeta `resultados/imagen_XX/` por imagen con las tablas, gráficos y resúmenes.

### Uso programático (ejemplo)

```python
from mejoraImagenes import ImageEnhancer

enh = ImageEnhancer('ruta/a/tu_imagen.jpg')
df = enh.generar_reporte_final(output_dir='resultados/mi_imagen')
# También puedes llamar a métodos individuales: enh.clahe(), enh.correccion_gamma(gamma=0.4), etc.
```

## Salidas generadas 📁

- `resultados/imagen_XX/metricas_completas.csv` (CSV)
- `resultados/imagen_XX/metricas_completas.xlsx` (Excel)
- `resultados/imagen_XX/metricas_completas.tex` (LaTeX)
- `resultados/imagen_XX/graficos_comparativos.png` (gráficos)
- `resultados/imagen_XX/resumen_imagen_XX.csv` (resumen por imagen)
- `resultados/imagen_XX/resumen_estadistico.csv` (resumen por categoría)

> Nota: los valores de PSNR y SSIM se calculan respecto a la imagen original (referencia). El script incluye recomendaciones automáticas basadas en las métricas (p. ej. usar CLAHE para bajo contraste, gamma < 1 para aclarar imágenes muy oscuras, promediado para reducir ruido).

## Contribuciones 🤝

Si quieres mejorar el repositorio, abre un issue o haz un pull request. Ideas útiles:

- Añadir filtros de denoising (Non-Local Means, BM3D)
- Más métricas perceptuales
- Soporte para procesamiento por lotes en paralelo

## Licencia 📄

Este proyecto está disponible bajo la licencia **MIT**.

## Contacto

Para dudas o sugerencias, abre un issue o contacta al autor del repositorio.
