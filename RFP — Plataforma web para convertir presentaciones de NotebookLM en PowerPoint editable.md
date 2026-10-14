# RFP — Plataforma web para convertir presentaciones de NotebookLM en PowerPoint editable

Oct 14, 2026 · @Erick Duvan Soto Diaz

## 1. Información general

Se solicitan propuestas para construir una aplicación web donde el usuario carga una presentación exportada por NotebookLM y descarga un PowerPoint con los textos editables, conservando el fondo, las imágenes, los colores y la jerarquía tipográfica originales. La lógica de conversión ya existe como la skill `notebooklm-pptx-editable` (Python); el proveedor debe convertirla en un producto con interfaz, servicio de procesamiento y revisión asistida.

| Campo | Valor |
| --- | --- |
| Nombre del proyecto | NLM Editable — Conversor de presentaciones NotebookLM a PPTX editable |
| Entidad solicitante | PersonalSoft (por confirmar) |
| Responsable técnico | Erick Duvan |
| Fecha de emisión | 14 de octubre de 2026 |
| Modalidad | Desarrollo de producto mínimo viable (MVP) con evolución posterior |
| Base técnica de referencia | Skill `notebooklm-pptx-editable`: CLI `nlm2pptx.py` con módulos `extract`, `ocr`, `clean`, `build` y `compare` |
| Entrada | `.pptx` exportado por NotebookLM (opcional en fase 2: `.pdf`) |
| Salida | `.pptx` editable, compatible con PowerPoint de escritorio y Google Slides |

Preguntas abiertas: fecha límite de recepción de propuestas, presupuesto de referencia y si la solución será de uso interno o comercial.

## 2. Contexto y problema

NotebookLM exporta cada diapositiva como una sola imagen a pantalla completa, así que el texto no se puede corregir, traducir ni reutilizar. Hoy la única salida es rehacer el deck a mano, lo que pierde el estilo visual que NotebookLM generó.

La skill `notebooklm-pptx-editable` ya resuelve el problema en un entorno con Claude y línea de comandos: reconstruye cada slide en tres capas (fondo sin texto, cuadros de texto nativos en la misma posición y notas del orador). Su limitación es operativa: exige instalar Python, Tesseract y LibreOffice, ejecutar comandos y editar a mano un archivo `layout.json` para corregir el OCR.

El software solicitado debe llevar esa misma calidad a cualquier usuario mediante una pantalla de carga, un procesamiento automático y una revisión visual, sin instalar nada ni editar JSON.

## 3. Objetivos y alcance

El objetivo es que un usuario sin conocimientos técnicos convierta un deck de NotebookLM en un PPTX editable en menos de 5 minutos para 20 diapositivas, con texto revisado y apariencia casi idéntica al original.

Objetivos específicos:

1. Ofrecer una pantalla de carga de archivos `.pptx` con validación de formato y tamaño.
2. Ejecutar el pipeline de la skill (extracción, OCR, limpieza de fondo, armado) como servicio.
3. Reemplazar la edición manual de `layout.json` por un editor visual de bloques de texto.
4. Mostrar la comparativa original contra editable antes de descargar.
5. Entregar un `.pptx` con fondo limpio como fondo de diapositiva, cuadros de texto nativos, título en el marcador de título y notas del orador conservadas.

| Incluido en el MVP | Excluido del MVP |
| --- | --- |
| Carga de `.pptx` de NotebookLM | Entrada `.pdf` (fase 2) |
| OCR en español e inglés | Traducción automática del contenido |
| Editor visual de texto, estilo y cajas | Edición de imágenes o ilustraciones |
| Selección de fuente equivalente | Instalación de fuentes en el equipo del usuario |
| Corrección ortográfica asistida por LLM (opcional, configurable) | Generación de diapositivas nuevas |
| Descarga del `.pptx` y del reporte de conversión | Integración directa con Google Drive o SharePoint (fase 2) |
| Historial de conversiones del usuario | Colaboración multiusuario en tiempo real |

## 4. Línea base técnica: la skill de referencia

El proveedor debe reutilizar los algoritmos de la skill como núcleo de procesamiento y envolverlos en un servicio; reescribirlos solo se acepta si demuestra igual o mejor calidad en el set de pruebas. La skill tiene unas 1.060 líneas de Python repartidas en cinco módulos y depende de `python-pptx`, `opencv-python-headless`, `numpy`, `Pillow`, `lxml` y Tesseract OCR; LibreOffice y poppler son opcionales.

| Fase | Módulo | Qué hace hoy | Qué debe aportar el producto |
| --- | --- | --- | --- |
| 1a. Extracción | `extract.py` | Saca la imagen de cada slide del PPTX; si un slide no es una sola imagen, lo renderiza completo con LibreOffice | Ejecución en servidor, aviso visible al usuario cuando se use el render alterno |
| 1b. OCR y estilo | `ocr.py` | Tesseract con agrupación propia en líneas y bloques; estima tamaño, color, negrita (grosor de trazo), alineación, viñetas e interlineado; unifica tamaños parecidos | Barra de progreso por slide, resaltado de bloques de baja confianza |
| Revisión | `layout.json` editado a mano | Corrección de texto, agrupación, viñetas, estilo, fuente y rol de título | Editor visual que escribe el mismo esquema `layout.json` |
| 2a. Limpieza | `clean.py` | Borra el texto del fondo con relleno por polinomio 2D en fondos lisos o en degradado, e inpainting en texturas | Vista previa del fondo limpio y opción de dejar un bloque como imagen |
| 2b. Armado | `build.py` | Fondo limpio como fondo de diapositiva (no seleccionable), cuadros de texto nativos, marcador de título, viñetas, notas | Generación en servidor y descarga |
| 2c. Verificación | `compare.py` | Render con LibreOffice y hoja lado a lado original contra editable | Comparador interactivo con deslizador por slide |

El contrato de datos entre fases es `layout.json` (coordenadas en píxeles de la imagen original, tamaños en puntos, colores en hex). El producto debe mantener ese esquema como formato interno versionado para que la CLI y la aplicación sigan siendo compatibles.

## 5. Flujo de usuario y pantallas

La aplicación tiene cuatro pantallas y un ciclo de ajuste: el usuario carga, espera el análisis, revisa los bloques detectados y compara contra el original hasta aprobar la descarga.

&#91;embedded content: flujo del usuario · 5 pantallas, 1 ciclo de ajuste\]

El ciclo entre revisión y comparación reemplaza las iteraciones manuales de `layout.json` y `build` de la skill; el modo rápido equivale a `nlm2pptx.py all`.

| Pantalla | Contenido principal | Requerimientos |
| --- | --- | --- |
| Carga | Zona de arrastrar y soltar, selector de archivo, límites visibles, idioma de OCR, fuente o destino de edición, botones Convertir y Modo rápido | RF-01 a RF-07, RF-11 |
| Procesamiento | Fases (extracción, OCR, limpieza) con barra por slide, miniaturas a medida que terminan, botón Cancelar | RF-08 a RF-10 |
| Revisión | Lista de slides a la izquierda; lienzo central con la imagen original y los bloques superpuestos; panel derecho con texto, estilo, rol, viñetas y la opción Dejar como imagen; sugerencias ortográficas | RF-12 a RF-24 |
| Comparación y descarga | Deslizador original contra editable por slide, advertencias, descarga del `.pptx` y del reporte | RF-25 a RF-30 |

## 6. Requerimientos funcionales

Se definen 34 requerimientos: 19 obligatorios para el MVP, 12 deseables y 3 opcionales. La prioridad sigue MoSCoW; los nombres de campo entre comillas invertidas son los del esquema `layout.json`.

| ID | Módulo | Requerimiento | Prioridad |
| --- | --- | --- | --- |
| RF-01 | Carga | Pantalla de carga con arrastrar y soltar y selector de archivo | Obligatorio |
| RF-02 | Carga | Aceptar solo `.pptx` y rechazar otros formatos con un mensaje claro | Obligatorio |
| RF-03 | Carga | Validar tamaño máximo (200 MB) y número de slides (60), ambos configurables | Obligatorio |
| RF-04 | Carga | Detectar si el archivo es de tipo NotebookLM (una imagen por slide) y avisar si no lo es | Obligatorio |
| RF-05 | Carga | Elegir idiomas de OCR antes de procesar (por defecto español e inglés) | Deseable |
| RF-06 | Carga | Indicar la fuente corporativa o el destino de edición (PowerPoint o Google Slides) para sugerir la fuente equivalente | Deseable |
| RF-07 | Carga | Aceptar `.pdf` exportado por NotebookLM | Opcional |
| RF-08 | Procesamiento | Ejecutar extracción, OCR y limpieza de forma asíncrona en una cola de trabajos | Obligatorio |
| RF-09 | Procesamiento | Mostrar el progreso por fase y por slide en tiempo real | Obligatorio |
| RF-10 | Procesamiento | Cancelar un trabajo en curso | Deseable |
| RF-11 | Procesamiento | Modo rápido: convertir sin revisión, con aviso de que el texto no está revisado | Deseable |
| RF-12 | Procesamiento | Corrección ortográfica asistida por LLM (tildes, ñ, comillas, guiones) presentada como sugerencias que el usuario acepta o rechaza | Deseable |
| RF-13 | Editor | Ver cada slide con los bloques detectados superpuestos, su id y en rojo los de baja confianza | Obligatorio |
| RF-14 | Editor | Editar el texto de cada párrafo en un panel lateral | Obligatorio |
| RF-15 | Editor | Editar estilo del bloque o párrafo: tamaño, color, negrita, cursiva, alineación y fuente | Obligatorio |
| RF-16 | Editor | Mover y redimensionar la caja de texto arrastrando (`box_px`) | Obligatorio |
| RF-17 | Editor | Unir bloques que son un mismo párrafo y dividir los que el OCR mezcló | Obligatorio |
| RF-18 | Editor | Activar viñetas y nivel por párrafo | Obligatorio |
| RF-19 | Editor | Dejar un bloque como parte de la imagen (`skip` y `remove_from_background: false`) | Obligatorio |
| RF-20 | Editor | Dibujar zonas de borrado adicionales para restos del texto viejo (`erase_boxes_px`) | Deseable |
| RF-21 | Editor | Asignar el rol de título, uno por slide | Obligatorio |
| RF-22 | Editor | Cambios en lote: fuente global y tamaño uniforme de títulos en todo el deck | Deseable |
| RF-23 | Editor | Editar las notas del orador | Opcional |
| RF-24 | Editor | Deshacer, rehacer y guardado automático | Deseable |
| RF-25 | Generación | Construir el `.pptx` con el fondo limpio como fondo de diapositiva y cuadros de texto nativos | Obligatorio |
| RF-26 | Generación | Comparador original contra editable por slide, con deslizador y vista lado a lado | Obligatorio |
| RF-27 | Generación | Reconstruir solo los slides modificados | Deseable |
| RF-28 | Generación | Validar la estructura OOXML del archivo antes de habilitar la descarga | Obligatorio |
| RF-29 | Entrega | Descargar el archivo como `<nombre>_editable.pptx` | Obligatorio |
| RF-30 | Entrega | Reporte de conversión: slides, bloques editables, bloques dejados como imagen y advertencias | Deseable |
| RF-31 | Entrega | Historial de conversiones con opción de reabrir el editor | Deseable |
| RF-32 | Entrega | Exportar e importar `layout.json` para compatibilidad con la CLI | Opcional |
| RF-33 | Administración | Inicio de sesión con SSO corporativo (Microsoft Entra ID) | Obligatorio |
| RF-34 | Administración | Panel de uso: conversiones, tiempos, errores y estado de la cola | Deseable |

## 7. Requerimientos no funcionales

Los valores son metas de referencia; el proveedor puede proponer otros si los justifica con mediciones.

| ID | Atributo | Requerimiento | Meta medible |
| --- | --- | --- | --- |
| RNF-01 | Rendimiento | Tiempo de análisis (extracción + OCR) de un deck de 20 slides | ≤ 90 s en p95 |
| RNF-02 | Rendimiento | Tiempo de reconstrucción tras editar | ≤ 15 s por deck de 20 slides; ≤ 3 s por slide individual |
| RNF-03 | Rendimiento | Respuesta del editor al mover o editar un bloque | ≤ 100 ms |
| RNF-04 | Escalabilidad | Procesamiento concurrente con workers que escalan según la cola | 20 trabajos simultáneos sin degradar RNF-01 |
| RNF-05 | Disponibilidad | Disponibilidad mensual del servicio | ≥ 99,5 % |
| RNF-06 | Compatibilidad | El `.pptx` abre sin reparaciones en PowerPoint 365 (Windows y macOS) y Google Slides | 100 % del set de pruebas |
| RNF-07 | Compatibilidad | Navegadores soportados | Últimas 2 versiones de Chrome, Edge, Firefox y Safari |
| RNF-08 | Usabilidad | Un usuario nuevo completa una conversión sin ayuda | ≥ 90 % en prueba con 10 usuarios |
| RNF-09 | Accesibilidad | Interfaz web accesible; cada slide de salida conserva su título en el marcador de título | WCAG 2.1 AA |
| RNF-10 | Idioma | Interfaz en español con soporte para inglés | Textos externalizados (i18n) |
| RNF-11 | Observabilidad | Logs estructurados, trazas por trabajo y métricas por fase | Correlación por id de trabajo |
| RNF-12 | Mantenibilidad | Núcleo de procesamiento como paquete Python versionado y compartido con la CLI | Cobertura de pruebas ≥ 80 % en el núcleo |
| RNF-13 | Portabilidad | Despliegue en contenedores con dependencias del sistema incluidas (Tesseract, LibreOffice, fuentes) | Imagen reproducible con versiones fijadas |

## 8. Arquitectura de referencia

Se propone una arquitectura de servicios con procesamiento asíncrono: la API recibe el archivo y encola el trabajo, y workers aislados ejecutan el núcleo de la skill empaquetado como librería Python. Es una referencia; el proveedor puede proponer otra si cumple los RNF.

&#91;embedded content: arquitectura de referencia · 8 componentes\]

Los workers llevan Tesseract (con modelos de español e inglés), LibreOffice y las fuentes de reemplazo en la imagen del contenedor. La caja punteada es opcional: solo recibe texto, nunca imágenes. El progreso llega al navegador por Server-Sent Events.

| Componente | Opción en AWS | Opción en Azure |
| --- | --- | --- |
| Frontend web | S3 + CloudFront | Static Web Apps |
| API y workers | ECS Fargate o EKS | Container Apps o AKS |
| Cola de trabajos | SQS | Service Bus |
| Base de datos | RDS PostgreSQL | Azure Database for PostgreSQL |
| Almacenamiento | S3 con cifrado KMS | Blob Storage con cifrado gestionado |
| Identidad | Entra ID vía OIDC | Entra ID |
| LLM opcional | Amazon Bedrock | Azure OpenAI o Azure AI Foundry |
| Observabilidad | CloudWatch + X-Ray | Azure Monitor + Application Insights |

## 9. Seguridad, privacidad y manejo de archivos

Las presentaciones pueden contener información confidencial de clientes, por lo que ningún archivo debe salir del entorno controlado sin autorización explícita.

- **Autenticación y autorización:** SSO con Microsoft Entra ID (OIDC); cada usuario ve solo sus conversiones; rol administrador separado.
- **Validación de entrada:** verificación de tipo real del archivo (no solo extensión), límite de tamaño, defensa contra ZIP bombs y XML External Entities al abrir el OOXML, y escaneo antivirus antes de procesar.
- **Aislamiento:** LibreOffice y Tesseract se ejecutan en workers sin red de salida, con usuario no privilegiado y límites de CPU, memoria y tiempo por trabajo.
- **Cifrado:** TLS 1.2+ en tránsito; cifrado en reposo con llaves gestionadas por la nube; URLs de descarga firmadas con expiración de 15 minutos.
- **Retención:** originales, imágenes intermedias y resultados se eliminan a los 7 días (configurable); el usuario puede borrar una conversión de inmediato.
- **LLM opcional (RF-12):** solo se envía el texto extraído, nunca las imágenes; el servicio debe ser corporativo, sin retención para entrenamiento, y la función debe poder desactivarse por política.
- **Auditoría:** registro de quién cargó, editó, descargó y eliminó cada archivo.
- **Pruebas:** modelado de amenazas STRIDE sobre el flujo de carga y procesamiento, y análisis contra OWASP Top 10 antes de salir a producción.

## 10. Criterios de aceptación y calidad

La solución se acepta cuando supera estas métricas sobre un set de 15 decks reales de NotebookLM (unas 250 slides) que entregará el solicitante, con estilos de fondo liso, degradado, textura y fotografía.

| Criterio | Cómo se mide | Umbral de aceptación |
| --- | --- | --- |
| Precisión del OCR antes de revisión | Tasa de error por carácter (CER) contra transcripción manual | ≤ 3 % en español con tildes y ñ |
| Precisión tras revisión asistida (RF-12) | CER tras aceptar sugerencias, sin edición manual | ≤ 1 % |
| Cobertura de texto editable | Bloques de texto del original convertidos en cuadros nativos | ≥ 95 % (excluye los marcados como imagen) |
| Fidelidad visual | SSIM entre original y editable renderizado, por slide | ≥ 0,92 en fondos lisos o en degradado; ≥ 0,85 en texturas |
| Limpieza del fondo | Slides sin restos visibles del texto viejo, en revisión humana | ≥ 95 % |
| Posición del texto | Desplazamiento del cuadro respecto al original | ≤ 2 % del ancho del slide |
| Integridad del archivo | Apertura sin reparación en PowerPoint 365 y Google Slides | 100 % |
| Notas y títulos | Notas del orador conservadas y un título por slide en su marcador | 100 % |

La paridad con la skill es requisito mínimo: en ningún deck del set la aplicación puede producir un resultado peor que la CLI `nlm2pptx.py all` con los mismos parámetros.

## 11. Entregables y cronograma indicativo

Se espera un MVP en producción en 12 semanas, con un gate tras la prueba de concepto y otro de aceptación final. Los proponentes pueden ajustar la duración si la justifican.

&#91;embedded content: cronograma indicativo · 4 fases, 2 gates\]

La entrada PDF, la integración con Google Drive o SharePoint y los requerimientos opcionales quedan para una fase de evolución posterior.

| Entregable | Fase |
| --- | --- |
| Núcleo de procesamiento empaquetado, con pruebas y compatible con la CLI | 0 |
| Informe de la prueba de concepto con métricas de la sección 10 | 0 |
| Código fuente en el repositorio del solicitante e infraestructura como código | 1 a 3 |
| Documento de arquitectura y modelo de amenazas | 1 |
| Aplicación web desplegada en ambientes de pruebas y producción | 2 y 3 |
| Manual de usuario y guía de operación | 3 |
| Informe de pruebas de aceptación, rendimiento y seguridad | 3 |
| Transferencia de conocimiento al equipo del solicitante | 3 |

## 12. Supuestos, restricciones y riesgos

Supuestos: NotebookLM sigue exportando una imagen por slide; el solicitante entrega el código de la skill y el set de pruebas; la solución se despliega en la nube corporativa del solicitante.

Restricciones: no se puede recuperar la fuente original de NotebookLM, por lo que se usa una equivalente instalada; el borrado sobre fotografías puede dejar una mancha leve; el render de verificación con LibreOffice puede diferir levemente de PowerPoint en saltos de línea.

| Riesgo | Impacto | Mitigación esperada |
| --- | --- | --- |
| NotebookLM cambia su formato de exportación | Alto | Detector de formato (RF-04), plan B de render completo y pruebas de regresión con decks nuevos cada mes |
| OCR deficiente en fuentes grandes, tildes o fondos con poco contraste | Alto | Corrección asistida por LLM (RF-12), resaltado de baja confianza (RF-13) y preprocesamiento de imagen |
| Manchas del inpainting sobre ilustraciones o fotos | Medio | Opción de dejar el bloque como imagen (RF-19) y zonas de borrado manuales (RF-20) |
| Saltos de línea distintos por fuente sustituta | Medio | Ajuste automático de tamaño o caja y selector de fuente según destino (RF-06) |
| Consumo alto de CPU y memoria de LibreOffice | Medio | Workers aislados con límites, timeouts y escalado por cola |
| Fuga de información confidencial | Alto | Controles de la sección 9 y desactivación del LLM por política |

## 13. Instrucciones para proponentes y evaluación

Cada propuesta debe incluir:

1. Entendimiento del problema y del pipeline de la skill.
2. Arquitectura propuesta con diagrama, stack y justificación de cada componente.
3. Matriz de cumplimiento contra RF-01 a RF-34 y RNF-01 a RNF-13 (cumple, cumple parcial, no cumple).
4. Prototipo del editor (mockups navegables de las cuatro pantallas).
5. Prueba de concepto: conversión de 3 decks del set entregados por el solicitante, con el `.pptx` resultante y las métricas de la sección 10.
6. Plan de trabajo, equipo con perfiles y dedicación, y supuestos.
7. Costo total (desarrollo y operación mensual estimada en la nube) y garantía.

| Criterio | Peso |
| --- | --- |
| Calidad técnica de la conversión en la prueba de concepto | 35 % |
| Arquitectura, seguridad y operabilidad | 20 % |
| Experiencia de usuario del editor | 15 % |
| Plan, equipo y experiencia comprobable | 10 % |
| Costo total de propiedad a 2 años | 20 % |

Preguntas abiertas para el solicitante: fecha de cierre de recepción, canal de preguntas de los proponentes y nube de despliegue definitiva.
