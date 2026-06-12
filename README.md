---
title: BioVerify Zero
emoji: 🔐
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# BioVerify-Zero v0.2.0-face-embedding-demo

## Verificación facial 1:1 con embeddings temporales y privacidad sin almacenamiento

**Autor:** Antonio Nicolás Toro González  
**Programa:** Maestría en Inteligencia Artificial para la Transformación Digital  
**Landing Page:** https://skepsis-apps.github.io/landing_page/

---

## 1. Visión general

BioVerify-Zero v2 mantiene la estructura funcional de la v1, pero reemplaza el extractor demostrativo por un pipeline de verificación facial 1:1 basado en:

```text
detección facial robusta
  ↓
alineación facial
  ↓
embedding facial temporal
  ↓
similitud coseno
  ↓
threshold
  ↓
match / no_match
```

La aplicación compara una imagen facial tomada de un documento con un fotograma capturado desde la cámara del usuario.

El procesamiento se realiza en backend y no existe almacenamiento deliberado de imágenes, documentos ni embeddings.

---

## 2. Arquitectura pública

```text
Usuario
  ↓
Navegador web
  ↓
Frontend HTML/CSS/JavaScript
  ↓
POST /api/v1/verify
  ↓
FastAPI
  ↓
OpenCV YuNet + SFace
  ↓
Embedding documento vs embedding vivo
  ↓
Respuesta JSON + resultado visual match / no_match
```

La versión pública no requiere Cloudflare Tunnel. El despliegue se realiza en Hugging Face Spaces mediante Docker.

---

## 3. Qué cambia respecto a v1

### v1

```text
detección facial
  ↓
extracción demo no biométrica
  ↓
similitud aproximada
```

### v2

```text
YuNet
  ↓
detección facial con landmarks
  ↓
SFace
  ↓
embedding facial temporal
  ↓
similitud coseno
  ↓
match / no_match
```

El campo `model_mode` cambia a:

```text
face_embedding_no_storage
```

---

## 4. Flujo de usuario

```text
Usuario
  ↓
Declara mayoría de edad
  ↓
Acepta consentimiento
  ↓
Carga imagen del documento
  ↓
Activa cámara
  ↓
Captura fotograma
  ↓
Presiona Verificar
  ↓
Obtiene Resultado: match / no_match
```

---

## 5. Flujo técnico

```text
frontend/app.js
  ↓
document_image_b64 + live_image_b64
  ↓
POST /api/v1/verify
  ↓
FastAPI
  ↓
validación de consentimiento
  ↓
validación de imagen
  ↓
decodificación OpenCV
  ↓
YuNet: detección facial
  ↓
SFace: alineación + embedding
  ↓
similitud coseno
  ↓
respuesta JSON
  ↓
resultado visual en navegador
```

---

## 6. Backend v2

Endpoint principal:

```http
POST /api/v1/verify
```

Endpoint de salud:

```http
GET /health
```

Solicitud esperada:

```json
{
  "consent_accepted": true,
  "document_image_b64": "data:image/...",
  "live_image_b64": "data:image/..."
}
```

Respuesta esperada:

```json
{
  "verified": true,
  "similarity_score": 0.7421,
  "threshold": 0.65,
  "decision": "match",
  "quality": {
    "document_face_detected": true,
    "live_face_detected": true,
    "single_face_per_image": true,
    "minimum_quality_passed": true,
    "document_face_selected": "main_face",
    "live_face_count": 1,
    "document_face_area_ratio": 0.12,
    "live_face_area_ratio": 0.18,
    "document_brightness_ok": true,
    "live_brightness_ok": true,
    "document_sharpness_ok": true,
    "live_sharpness_ok": true
  },
  "retention": "no intentional biometric storage",
  "model_mode": "face_embedding_no_storage",
  "warning": "Prototipo académico. Procesamiento biométrico temporal sin almacenamiento deliberado. No usar para decisiones reales de identidad."
}
```

---

## 7. Privacidad y uso restringido

La integración tecnológica incluye:

- [x] Declaración de mayoría de edad.
- [x] Consentimiento explícito.
- [x] No uso de base de datos.
- [x] No almacenamiento deliberado de imágenes.
- [x] No almacenamiento deliberado de documentos.
- [x] No almacenamiento deliberado de embeddings.
- [x] No entrenamiento con imágenes del usuario.
- [x] Logs estructurados sin imágenes ni embeddings.
- [x] Respuesta limitada a score, decisión y controles de calidad.

La aplicación declara:

```text
retention: no intentional biometric storage
model_mode: face_embedding_no_storage
```

BioVerify-Zero v2 realiza procesamiento biométrico temporal para fines demostrativos, pero no persiste imágenes, documentos ni embeddings.

---

## 8. Modelos utilizados

La v2 usa modelos ONNX del OpenCV Zoo:

```text
models/face_detection_yunet_2023mar.onnx
models/face_recognition_sface_2021dec.onnx
```

Durante el build Docker se ejecuta:

```bash
python scripts/download_models.py
```

Ese script descarga los modelos en `models/`.

---

## 9. Configuración principal

Variables relevantes:

```env
APP_MODE=face_embedding_demo
SIMILARITY_THRESHOLD=0.65

FACE_DETECTOR_MODE=yunet
FACE_EMBEDDING_MODE=sface

YUNET_MODEL_PATH=models/face_detection_yunet_2023mar.onnx
SFACE_MODEL_PATH=models/face_recognition_sface_2021dec.onnx

YUNET_SCORE_THRESHOLD=0.85
YUNET_NMS_THRESHOLD=0.30
YUNET_TOP_K=5000

MIN_FACE_AREA_RATIO=0.015
MIN_BLUR_SCORE=18.0
MIN_BRIGHTNESS=35.0
MAX_BRIGHTNESS=225.0
```

---

## 10. Arquitectura modular

```text
bioverify-zero/
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── verify_routes.py
│   │   └── health_routes.py
│   │
│   ├── schemas/
│   │   ├── verify_response.py
│   │   └── error_response.py
│   │
│   ├── services/
│   │   ├── image_validation.py
│   │   ├── image_decoder.py
│   │   ├── face_detection.py
│   │   ├── face_quality.py
│   │   ├── embedding_extractor.py
│   │   ├── face_verifier.py
│   │   └── memory_cleanup.py
│   │
│   ├── security/
│   │   ├── upload_guards.py
│   │   ├── cors_policy.py
│   │   └── privacy_guards.py
│   │
│   └── legal/
│
├── frontend/
│   ├── index.html
│   └── app.js
│
├── models/
│   └── .gitkeep
│
├── scripts/
│   └── download_models.py
│
├── tests/
├── Dockerfile
├── requirements.txt
├── README.md
└── .env.example
```

---

## 11. Ejecución local

Crear entorno virtual:

```bash
py -3.12 -m venv .venv
```

Activar entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Descargar modelos:

```bash
python scripts/download_models.py
```

Ejecutar:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

Abrir:

```text
http://localhost:7860
```

---

## 12. Despliegue

Flujo DevOps:

```text
Código local
  ↓
git commit
  ↓
push a GitHub
  ↓
push a Hugging Face Space
  ↓
Docker build automático
  ↓
contenedor público
  ↓
URL .hf.space
```

Repositorios y servicios:

```text
GitHub:
https://github.com/antoniot73/bioverify-zero-v2

Hugging Face Space:
https://huggingface.co/spaces/antoniot73/bioverify-zero

Aplicación pública:
https://antoniot73-bioverify-zero.hf.space

Health check:
https://antoniot73-bioverify-zero.hf.space/health
```

---

## 13. Contenerización

El sistema usa Docker con:

```text
Base image: python:3.11-slim
Servidor: uvicorn
Framework API: FastAPI
Puerto expuesto: 7860
Usuario no root: appuser
Procesamiento visual: opencv-contrib-python-headless + numpy
Modelos: YuNet + SFace ONNX
```

El puerto `7860` se alinea con Hugging Face Spaces.

---

## 14. Aviso de uso restringido

BioVerify-Zero v2 es un prototipo académico y demostrativo.

No debe utilizarse para:

- decisiones reales de identidad,
- autenticación productiva,
- procesos legales,
- verificación financiera,
- control de acceso real,
- sistemas biométricos productivos.

---

## 15. Créditos

**Autor:** Antonio Nicolás Toro González  
**Maestría:** Maestría en Inteligencia Artificial para la Transformación Digital  
**Landing Page:** https://skepsis-apps.github.io/landing_page/
