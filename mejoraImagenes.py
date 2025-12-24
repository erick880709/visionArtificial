"""
==============================================================================
LABORATORIO: MEJORA DE IMAGEN - OPERACIONES ELEMENTALES
Universidad de La Rioja - Maestría en IA
Visión Artificial

Dataset: The Dark Face - Imágenes con baja iluminación nocturna

MODIFICADO PARA GENERAR REPORTE DE MÉTRICAS POR TÉCNICA
==============================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
from pathlib import Path
import os
import io
import warnings
import glob
import random
import pandas as pd
import seaborn as sns
from scipy import stats
warnings.filterwarnings('ignore')

try:
    import kagglehub
    KAGGLEHUB_AVAILABLE = True
except ImportError:
    KAGGLEHUB_AVAILABLE = False
    print("⚠ kagglehub no está instalado. Para instalarlo ejecuta: pip install kagglehub")

# Configuración de visualización
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.size'] = 9
plt.rcParams['image.cmap'] = 'gray'
sns.set_palette("husl")

print("="*80)
print("LABORATORIO: MEJORA DE IMAGEN - OPERACIONES ELEMENTALES")
print("Dataset: The Dark Face")
print("Universidad de La Rioja - Maestría en IA")
print("="*80)

# ==============================================================================
# CLASE PRINCIPAL PARA MEJORA DE IMAGEN CON MÉTRICAS
# ==============================================================================

class ImageEnhancer:
    """Clase para aplicar técnicas de mejora de imagen con métricas detalladas"""
    
    def __init__(self, image_path):
        """
        Inicializa el procesador de imágenes
        Args:
            image_path: Ruta de la imagen a procesar
        """
        self.original = cv2.imread(image_path)
        if self.original is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")
        
        # Convertir BGR a RGB para visualización correcta
        self.original_rgb = cv2.cvtColor(self.original, cv2.COLOR_BGR2RGB)
        self.gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        self.results = {}
        self.metrics_df = pd.DataFrame()  # DataFrame para almacenar métricas
        
        print(f"✓ Imagen cargada: {self.gray.shape}")
        print(f"  Rango de valores original: [{self.gray.min()}, {self.gray.max()}]")
        print(f"  Media original: {np.mean(self.gray):.2f}, Desviación estándar: {np.std(self.gray):.2f}")
    
    # ==================== MÉTRICAS DE CALIDAD MEJORADAS ====================
    
    def calcular_metricas_completas(self, img, nombre_tecnica):
        """
        Calcula métricas de calidad de imagen completas.
        
        Args:
            img: Imagen a evaluar
            nombre_tecnica: Nombre de la técnica aplicada
            
        Returns:
            dict: Diccionario con todas las métricas calculadas
        """
        # Métricas básicas
        media = np.mean(img)
        desviacion = np.std(img)
        minimo = np.min(img)
        maximo = np.max(img)
        rango_dinamico = maximo - minimo
        
        # Métricas de contraste
        contraste_rms = np.sqrt(np.mean((img - media) ** 2))
        
        # Métricas de histograma
        hist, _ = np.histogram(img.flatten(), bins=256, range=(0, 256))
        hist_norm = hist / hist.sum()
        hist_norm = hist_norm[hist_norm > 0]
        entropia = -np.sum(hist_norm * np.log2(hist_norm))
        
        # PSNR (Peak Signal-to-Noise Ratio) respecto a la original
        if nombre_tecnica != "Original":
            mse = np.mean((self.gray.astype(float) - img.astype(float)) ** 2)
            psnr = 20 * np.log10(255 / np.sqrt(mse)) if mse > 0 else float('inf')
        else:
            psnr = float('inf')
        
        # SSIM (Structural Similarity Index)
        if nombre_tecnica != "Original":
            ssim_val = self._calcular_ssim(self.gray, img)
        else:
            ssim_val = 1.0
        
        # Coeficiente de variación (normalización por media)
        coef_variacion = (desviacion / media * 100) if media > 0 else 0
        
        # Kurtosis y Skewness
        kurtosis = stats.kurtosis(img.flatten())
        skewness = stats.skew(img.flatten())
        
        # Entropía diferencial (información añadida)
        if nombre_tecnica != "Original":
            entropia_diff = entropia - self._calcular_entropia(self.gray)
        else:
            entropia_diff = 0
        
        # Detección de bordes (medida de nitidez)
        sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
        magnitud_bordes = np.sqrt(sobel_x**2 + sobel_y**2)
        nitidez = np.mean(magnitud_bordes)
        
        # Agregar todas las métricas al diccionario
        metricas = {
            'Técnica': nombre_tecnica,
            'Media': media,
            'Desviación Estándar': desviacion,
            'Mínimo': minimo,
            'Máximo': maximo,
            'Rango Dinámico': rango_dinamico,
            'Contraste (RMS)': contraste_rms,
            'Entropía': entropia,
            'Δ Entropía': entropia_diff,
            'PSNR (dB)': psnr,
            'SSIM': ssim_val,
            'Coef. Variación (%)': coef_variacion,
            'Kurtosis': kurtosis,
            'Skewness': skewness,
            'Nitidez (Bordes)': nitidez,
            'Tipo': self._clasificar_tecnica(nombre_tecnica)
        }
        
        # Agregar al DataFrame
        nueva_fila = pd.DataFrame([metricas])
        self.metrics_df = pd.concat([self.metrics_df, nueva_fila], ignore_index=True)
        
        return metricas
    
    def _calcular_ssim(self, img1, img2):
        """Calcula el Structural Similarity Index"""
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2
        
        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)
        
        kernel = cv2.getGaussianKernel(11, 1.5)
        window = np.outer(kernel, kernel.transpose())
        
        mu1 = cv2.filter2D(img1, -1, window)[5:-5, 5:-5]
        mu2 = cv2.filter2D(img2, -1, window)[5:-5, 5:-5]
        
        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2
        
        sigma1_sq = cv2.filter2D(img1 ** 2, -1, window)[5:-5, 5:-5] - mu1_sq
        sigma2_sq = cv2.filter2D(img2 ** 2, -1, window)[5:-5, 5:-5] - mu2_sq
        sigma12 = cv2.filter2D(img1 * img2, -1, window)[5:-5, 5:-5] - mu1_mu2
        
        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
                   ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
        
        return np.mean(ssim_map)
    
    def _calcular_entropia(self, img):
        """Calcula la entropía de Shannon"""
        hist, _ = np.histogram(img.flatten(), bins=256, range=(0, 256))
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        return -np.sum(hist * np.log2(hist))
    
    def _clasificar_tecnica(self, nombre):
        """Clasifica la técnica en su categoría"""
        categorias = {
            'Original': 'Referencia',
            'Negativo': 'Ajuste Intensidad',
            'Logarítmica': 'Ajuste Intensidad',
            'Gamma': 'Ajuste Intensidad',
            'Estiramiento Lineal': 'Ajuste Intensidad',
            'Ecualización': 'Histograma',
            'CLAHE': 'Histograma',
            'Multiplicación': 'Aritmética',
            'Promediado': 'Aritmética',
            'Suma': 'Aritmética',
            'Resta': 'Aritmética'
        }
        
        for key, value in categorias.items():
            if key in nombre:
                return value
        return 'Otra'
    
    # ==================== 1. FUNCIONES DE AJUSTE DE INTENSIDAD ====================
    
    def negativo(self):
        """Transformación negativa"""
        L = 256
        img_negativa = (L - 1) - self.gray
        img_result = img_negativa.astype(np.uint8)
        
        # Calcular métricas
        metricas = self.calcular_metricas_completas(img_result, "Negativo")
        self.results['negativo'] = {'imagen': img_result, 'metricas': metricas}
        
        return img_result
    
    def transformacion_logaritmica(self, c=1.0):
        """Transformación logarítmica"""
        img_float = self.gray.astype(float)
        img_log = c * np.log(1 + img_float)
        img_log = ((img_log - img_log.min()) / 
                   (img_log.max() - img_log.min()) * 255)
        img_result = img_log.astype(np.uint8)
        
        metricas = self.calcular_metricas_completas(img_result, 
                                                   f"Logarítmica (c={c})")
        self.results[f'logaritmica_{c}'] = {'imagen': img_result, 'metricas': metricas}
        
        return img_result
    
    def correccion_gamma(self, gamma=2.2, c=1.0):
        """Corrección gamma"""
        img_norm = self.gray.astype(float) / 255.0
        img_gamma = c * np.power(img_norm, gamma)
        img_gamma = (img_gamma * 255).clip(0, 255)
        img_result = img_gamma.astype(np.uint8)
        
        gamma_type = "oscurecimiento" if gamma > 1 else "aclarado"
        metricas = self.calcular_metricas_completas(img_result, 
                                                   f"Gamma (γ={gamma}, {gamma_type})")
        self.results[f'gamma_{gamma}'] = {'imagen': img_result, 'metricas': metricas}
        
        return img_result
    
    def estiramiento_lineal(self, s_min=0, s_max=255):
        """Estiramiento lineal"""
        img_float = self.gray.astype(float)
        r_min = img_float.min()
        r_max = img_float.max()
        
        if r_max == r_min:
            return self.gray
        
        img_estirada = ((img_float - r_min) / (r_max - r_min) * 
                        (s_max - s_min) + s_min)
        img_result = img_estirada.astype(np.uint8)
        
        metricas = self.calcular_metricas_completas(img_result, "Estiramiento Lineal")
        self.results['estiramiento_lineal'] = {'imagen': img_result, 'metricas': metricas}
        
        return img_result
    
    # ==================== 2. PROCESAMIENTO DE HISTOGRAMA ====================
    
    def ecualizacion_histograma(self):
        """Ecualización de histograma estándar"""
        img_ecualizada = cv2.equalizeHist(self.gray)
        
        metricas = self.calcular_metricas_completas(img_ecualizada, "Ecualización")
        self.results['ecualizacion'] = {'imagen': img_ecualizada, 'metricas': metricas}
        
        return img_ecualizada
    
    def clahe(self, clip_limit=2.0, tile_size=(8, 8)):
        """CLAHE - Ecualización Adaptativa"""
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
        img_clahe = clahe.apply(self.gray)
        
        metricas = self.calcular_metricas_completas(img_clahe, 
                                                   f"CLAHE (clip={clip_limit})")
        self.results[f'clahe_{clip_limit}'] = {'imagen': img_clahe, 'metricas': metricas}
        
        return img_clahe
    
    # ==================== 3. OPERADORES ARITMÉTICOS ====================
    
    def multiplicacion_escalar(self, factor=1.5):
        """Multiplicación por escalar"""
        resultado = np.clip(self.gray.astype(float) * factor, 0, 255)
        img_result = resultado.astype(np.uint8)
        
        accion = "aclarado" if factor > 1 else "oscurecimiento"
        metricas = self.calcular_metricas_completas(img_result, 
                                                   f"Multiplicación ({factor}x, {accion})")
        self.results[f'multiplicacion_{factor}'] = {'imagen': img_result, 'metricas': metricas}
        
        return img_result
    
    def promediado_imagenes(self, lista_imagenes):
        """Promediado para reducción de ruido"""
        suma = self.gray.astype(float)
        n = 1
        
        for img in lista_imagenes:
            if img.shape != self.gray.shape:
                img = cv2.resize(img, (self.gray.shape[1], self.gray.shape[0]))
            suma += img.astype(float)
            n += 1
        
        promedio = (suma / n).astype(np.uint8)
        
        metricas = self.calcular_metricas_completas(promedio, 
                                                   f"Promediado ({n} imágenes)")
        self.results['promediado'] = {'imagen': promedio, 'metricas': metricas}
        
        return promedio
    
    # ==================== APLICACIÓN DE TODAS LAS TÉCNICAS ====================
    
    def aplicar_todas_tecnicas(self):
        """
        Aplica todas las técnicas y calcula métricas automáticamente.
        Devuelve un DataFrame completo con resultados.
        """
        print("\n" + "="*80)
        print("APLICANDO TÉCNICAS DE MEJORA DE IMAGEN")
        print("="*80)
        
        # Primero, calcular métricas de la imagen original
        self.calcular_metricas_completas(self.gray, "Original")
        
        print("\n[1/3] Aplicando Funciones de Ajuste de Intensidad...")
        self.negativo()
        self.transformacion_logaritmica(c=1.0)
        self.transformacion_logaritmica(c=2.0)
        self.correccion_gamma(gamma=0.4, c=1.0)   # Aclarado
        self.correccion_gamma(gamma=2.5, c=1.0)   # Oscurecimiento
        self.estiramiento_lineal()
        
        print("[2/3] Aplicando Procesamiento de Histograma...")
        self.ecualizacion_histograma()
        self.clahe(clip_limit=2.0)
        self.clahe(clip_limit=4.0)
        
        print("[3/3] Aplicando Operadores Aritméticos...")
        self.multiplicacion_escalar(1.5)  # Aclarado
        self.multiplicacion_escalar(0.7)  # Oscurecimiento
        
        # Simulación de promediado para reducción de ruido
        np.random.seed(42)  # Para reproducibilidad
        img_ruido1 = self.gray + np.random.normal(0, 15, self.gray.shape)
        img_ruido2 = self.gray + np.random.normal(0, 15, self.gray.shape)
        self.promediado_imagenes([
            np.clip(img_ruido1, 0, 255).astype(np.uint8),
            np.clip(img_ruido2, 0, 255).astype(np.uint8)
        ])
        
        print("✓ Todas las técnicas aplicadas y métricas calculadas")
        
        return self.metrics_df
    
    # ==================== GENERACIÓN DE REPORTES ====================
    
    def generar_tabla_metricas(self, output_dir='resultados'):
        """
        Genera una tabla completa de métricas en formato LaTeX, CSV y Excel.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Ordenar por tipo de técnica
        self.metrics_df = self.metrics_df.sort_values(['Tipo', 'Media'])
        
        # Guardar en diferentes formatos
        csv_path = f'{output_dir}/metricas_completas.csv'
        excel_path = f'{output_dir}/metricas_completas.xlsx'
        latex_path = f'{output_dir}/metricas_completas.tex'
        
        # CSV
        self.metrics_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Excel con formato
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            self.metrics_df.to_excel(writer, sheet_name='Métricas', index=False)
            
            # Formato condicional
            workbook = writer.book
            worksheet = writer.sheets['Métricas']
            
            # Formato para valores altos de PSNR (mejor)
            psnr_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
            worksheet.conditional_format('K2:K100', {
                'type': 'cell',
                'criteria': '>',
                'value': 30,
                'format': psnr_format
            })
        
        # LaTeX para informe académico
        latex_str = self.metrics_df.to_latex(index=False, 
                                           float_format="%.2f",
                                           caption="Métricas de calidad por técnica aplicada",
                                           label="tab:metricas")
        
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write(latex_str)
        
        print(f"\n✓ Tablas de métricas generadas en:")
        print(f"  - CSV: {csv_path}")
        print(f"  - Excel: {excel_path}")
        print(f"  - LaTeX: {latex_path}")
        
        return self.metrics_df
    
    def generar_resumen_estadistico(self, output_dir='resultados'):
        """
        Genera un resumen estadístico por categoría de técnica.
        """
        resumen = self.metrics_df.groupby('Tipo').agg({
            'Media': ['mean', 'std', 'min', 'max'],
            'Desviación Estándar': ['mean', 'std'],
            'Entropía': ['mean', 'std'],
            'PSNR (dB)': ['mean', 'max'],
            'SSIM': ['mean', 'min']
        }).round(2)
        
        resumen_path = f'{output_dir}/resumen_estadistico.csv'
        resumen.to_csv(resumen_path, encoding='utf-8-sig')
        
        print(f"\n✓ Resumen estadístico generado: {resumen_path}")
        
        return resumen
    
    def graficar_comparacion_metricas(self, output_dir='resultados'):
        """
        Genera gráficos comparativos de las métricas principales.
        """
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        fig.suptitle('Comparación de Métricas por Técnica', fontsize=16, fontweight='bold')
        
        # Gráfico 1: Media y Desviación Estándar
        axes[0, 0].bar(self.metrics_df['Técnica'], self.metrics_df['Media'], 
                       alpha=0.7, label='Media')
        axes[0, 0].errorbar(self.metrics_df['Técnica'], self.metrics_df['Media'],
                           yerr=self.metrics_df['Desviación Estándar']/2,
                           fmt='none', color='black', capsize=3, label='±½ Desv.Std')
        axes[0, 0].set_title('Media y Variabilidad')
        axes[0, 0].set_ylabel('Intensidad Media')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Gráfico 2: Contraste (RMS)
        axes[0, 1].bar(self.metrics_df['Técnica'], self.metrics_df['Contraste (RMS)'],
                       color='orange', alpha=0.7)
        axes[0, 1].set_title('Contraste (RMS)')
        axes[0, 1].set_ylabel('Contraste')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
        
        # Gráfico 3: Entropía
        axes[0, 2].bar(self.metrics_df['Técnica'], self.metrics_df['Entropía'],
                       color='green', alpha=0.7)
        axes[0, 2].axhline(y=self.metrics_df.loc[0, 'Entropía'], color='r', 
                          linestyle='--', label='Original')
        axes[0, 2].set_title('Entropía (Información)')
        axes[0, 2].set_ylabel('Entropía (bits)')
        axes[0, 2].tick_params(axis='x', rotation=45)
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)
        
        # Gráfico 4: PSNR
        axes[1, 0].bar(self.metrics_df['Técnica'][1:], self.metrics_df['PSNR (dB)'][1:],
                       color='blue', alpha=0.7)
        axes[1, 0].axhline(y=30, color='r', linestyle='--', label='Umbral Bueno (30dB)')
        axes[1, 0].set_title('PSNR (Calidad respecto a Original)')
        axes[1, 0].set_ylabel('PSNR (dB)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Gráfico 5: SSIM
        axes[1, 1].bar(self.metrics_df['Técnica'][1:], self.metrics_df['SSIM'][1:],
                       color='purple', alpha=0.7)
        axes[1, 1].axhline(y=0.9, color='r', linestyle='--', label='Excelente (>0.9)')
        axes[1, 1].set_title('SSIM (Similaridad Estructural)')
        axes[1, 1].set_ylabel('SSIM')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        # Gráfico 6: Rango Dinámico
        axes[1, 2].bar(self.metrics_df['Técnica'], self.metrics_df['Rango Dinámico'],
                       color='brown', alpha=0.7)
        axes[1, 2].set_title('Rango Dinámico')
        axes[1, 2].set_ylabel('Rango (Máx-Mín)')
        axes[1, 2].tick_params(axis='x', rotation=45)
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/graficos_comparativos.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Gráficos comparativos generados: {output_dir}/graficos_comparativos.png")
    
    def generar_reporte_final(self, output_dir='resultados'):
        """
        Genera un reporte final completo con todas las métricas, gráficos y análisis.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*80)
        print("GENERANDO REPORTE FINAL DE MÉTRICAS")
        print("="*80)
        
        # 1. Aplicar todas las técnicas
        df_metricas = self.aplicar_todas_tecnicas()
        
        # 2. Mostrar tabla en consola (formato reducido)
        print("\n📊 RESUMEN DE MÉTRICAS (Top 5 por PSNR):")
        print("-" * 100)
        top_psnr = df_metricas.nlargest(5, 'PSNR (dB)')[['Técnica', 'PSNR (dB)', 'SSIM', 'Entropía', 'Tipo']]
        print(top_psnr.to_string(index=False))
        
        print("\n📊 RESUMEN DE MÉTRICAS (Top 5 por Contraste):")
        print("-" * 100)
        top_contraste = df_metricas.nlargest(5, 'Contraste (RMS)')[['Técnica', 'Contraste (RMS)', 'Media', 'Desviación Estándar', 'Tipo']]
        print(top_contraste.to_string(index=False))
        
        # 3. Generar archivos
        self.generar_tabla_metricas(output_dir)
        self.generar_resumen_estadistico(output_dir)
        self.graficar_comparacion_metricas(output_dir)
        
        # 4. Análisis cualitativo automático
        print("\n" + "="*80)
        print("ANÁLISIS CUALITATIVO AUTOMÁTICO")
        print("="*80)
        
        # Mejor técnica por categoría
        categorias = df_metricas['Tipo'].unique()
        for categoria in categorias:
            if categoria != 'Referencia':
                df_cat = df_metricas[df_metricas['Tipo'] == categoria]
                if not df_cat.empty:
                    mejor_psnr = df_cat.loc[df_cat['PSNR (dB)'].idxmax()]
                    mejor_contraste = df_cat.loc[df_cat['Contraste (RMS)'].idxmax()]
                    
                    print(f"\n📍 CATEGORÍA: {categoria}")
                    print(f"   • Mejor PSNR: {mejor_psnr['Técnica']} ({mejor_psnr['PSNR (dB)']:.1f} dB)")
                    print(f"   • Mejor contraste: {mejor_contraste['Técnica']} ({mejor_contraste['Contraste (RMS)']:.1f})")
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES BASADAS EN MÉTRICAS:")
        
        # Para imágenes muy oscuras (media baja)
        if df_metricas.loc[0, 'Media'] < 50:
            print("   • Imagen muy oscura. Recomendado: Gamma (γ<1) o Multiplicación (>1)")
        
        # Para imágenes con poco contraste (desviación baja)
        if df_metricas.loc[0, 'Desviación Estándar'] < 30:
            print("   • Contraste bajo. Recomendado: CLAHE o Estiramiento Lineal")
        
        # Para imágenes con ruido (kurtosis alta)
        if df_metricas.loc[0, 'Kurtosis'] > 3:
            print("   • Posible ruido presente. Recomendado: Promediado o filtrado")
        
        print("\n✓ Reporte final generado exitosamente!")
        print(f"📁 Resultados en: {output_dir}/")
        
        return df_metricas


# ==============================================================================
# FUNCIONES AUXILIARES (sin cambios mayores)
# ==============================================================================

def descargar_dataset():
    """Descarga el dataset Dark Face desde Kaggle"""
    if not KAGGLEHUB_AVAILABLE:
        print("\n❌ Error: kagglehub no está instalado")
        print("📦 Para instalar ejecuta: pip install kagglehub")
        return None
    
    try:
        print("\n🔄 Descargando dataset Dark Face desde Kaggle...")
        path = kagglehub.dataset_download("soumikrakshit/dark-face-dataset")
        print(f"\n✓ Dataset descargado en: {path}")
        return path
    except Exception as e:
        print(f"\n❌ Error al descargar: {str(e)}")
        return None

def seleccionar_imagenes_dataset(dataset_path, num_imagenes=4):
    """Selecciona imágenes aleatoriamente del dataset"""
    if dataset_path is None:
        return None
    
    extensiones = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    imagenes = []
    
    for ext in extensiones:
        imagenes.extend(glob.glob(os.path.join(dataset_path, '**', ext), recursive=True))
    
    if len(imagenes) == 0:
        print(f"\n⚠ No se encontraron imágenes en: {dataset_path}")
        return None
    
    print(f"\n📊 Total de imágenes encontradas: {len(imagenes)}")
    
    if len(imagenes) < num_imagenes:
        imagenes_seleccionadas = imagenes
    else:
        imagenes_seleccionadas = random.sample(imagenes, num_imagenes)
    
    print(f"\n✓ Imágenes seleccionadas:")
    for idx, img_path in enumerate(imagenes_seleccionadas, 1):
        print(f"   {idx}. {os.path.basename(img_path)}")
    
    return imagenes_seleccionadas


# ==============================================================================
# FUNCIÓN PRINCIPAL MODIFICADA
# ==============================================================================

def main():
    """Función principal del laboratorio con métricas mejoradas"""
    
    print("="*80)
    print("LABORATORIO: MEJORA DE IMAGEN CON MÉTRICAS AVANZADAS")
    print("="*80)
    
    # Opciones de entrada (simplificado)
    print("\n📁 Selección de imágenes:")
    print("  1. Descargar dataset Dark Face")
    print("  2. Usar ruta local")
    print("  3. Usar imagen de prueba")
    
    opcion = input("\nSelecciona opción (1, 2 o 3): ").strip()
    
    imagenes_seleccionadas = []
    
    if opcion == "1":
        dataset_path = descargar_dataset()
        if dataset_path:
            imagenes_seleccionadas = seleccionar_imagenes_dataset(dataset_path, 4)
    
    elif opcion == "2":
        ruta_local = input("Ruta del dataset: ").strip()
        if os.path.exists(ruta_local):
            imagenes_seleccionadas = seleccionar_imagenes_dataset(ruta_local, 4)
    
    elif opcion == "3":
        # Crear imagen de prueba
        size = 512
        x = np.linspace(0, 2*np.pi, size)
        y = np.linspace(0, 2*np.pi, size)
        X, Y = np.meshgrid(x, y)
        img_test = (np.sin(X) * np.cos(Y) + 1) * 40
        img_test = img_test.astype(np.uint8)
        
        Path('temp_images').mkdir(exist_ok=True)
        image_path = 'temp_images/test_dark_image.jpg'
        cv2.imwrite(image_path, img_test)
        imagenes_seleccionadas = [image_path]
    
    if len(imagenes_seleccionadas) == 0:
        print("\n❌ No hay imágenes para procesar")
        return
    
    # Procesar cada imagen
    for idx, image_path in enumerate(imagenes_seleccionadas, 1):
        try:
            print(f"\n{'='*80}")
            print(f"📷 PROCESANDO IMAGEN {idx}: {os.path.basename(image_path)}")
            print(f"{'='*80}")
            
            output_dir = f'resultados/imagen_{idx:02d}'
            
            enhancer = ImageEnhancer(image_path)
            
            # Generar reporte completo con métricas
            df_metricas = enhancer.generar_reporte_final(output_dir=output_dir)
            
            # Guardar también un resumen específico para esta imagen
            resumen_img = df_metricas[['Técnica', 'Tipo', 'Media', 'Desviación Estándar', 
                                      'PSNR (dB)', 'SSIM', 'Entropía']]
            resumen_img.to_csv(f'{output_dir}/resumen_imagen_{idx:02d}.csv', index=False)
            
            print(f"\n✓ Imagen {idx} procesada. Métricas guardadas.")
            
        except Exception as e:
            print(f"\n❌ Error en imagen {idx}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Resumen final
    print(f"\n{'='*80}")
    print("✨ PROCESAMIENTO COMPLETADO")
    print(f"{'='*80}")
    print(f"\n📊 RESUMEN:")
    print(f"   • Imágenes procesadas: {len(imagenes_seleccionadas)}")
    print(f"   • Métricas generadas: En carpeta 'resultados/'")
    print(f"\n📁 ARCHIVOS GENERADOS:")
    print(f"   resultados/imagen_XX/")
    print(f"   ├── metricas_completas.csv/tex/xlsx")
    print(f"   ├── resumen_estadistico.csv")
    print(f"   ├── graficos_comparativos.png")
    print(f"   └── resumen_imagen_XX.csv")
    print(f"\n📝 PARA TU MEMORIA:")
    print(f"   1. Usa las tablas en CSV/Excel para importar a Word/LaTeX")
    print(f"   2. Incluye los gráficos generados")
    print(f"   3. Cita las métricas en tu análisis (PSNR, SSIM, Entropía)")
    print(f"   4. Usa las recomendaciones automáticas como guía")
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()