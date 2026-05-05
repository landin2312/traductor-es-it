# Traduttore Spagnolo → Italiano

Aplicación web de traducción español-italiano usando el modelo base **Qwen/Qwen2-0.5B** de Hugging Face con inferencia local. Sin APIs externas.

## Estructura del proyecto

```
traductor_es_it/
├── backend/
│   ├── app.py            # Servidor Flask con el modelo
│   └── requirements.txt  # Dependencias Python
├── frontend/
│   └── index.html        # Interfaz completa (HTML + CSS + JS)
└── README.md
```

## Requisitos previos

- Python 3.9 o superior
- pip
- Conexión a internet (solo para descargar el modelo la primera vez, ~1 GB)

## Instalación y ejecución

### 1. Instalar dependencias del backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Iniciar el servidor Flask

```bash
python app.py
```

La primera vez descargará el modelo **Qwen/Qwen2-0.5B** (~1 GB). Una vez cargado verás:

```
Model loaded successfully.
 * Running on http://0.0.0.0:5000
```

### 3. Abrir el frontend

Abre el archivo `frontend/index.html` directamente en tu navegador (doble clic). No necesita servidor web propio.

El indicador de estado en la interfaz cambiará a **verde** cuando el servidor esté listo.

## Uso

1. Escribe texto en español en el área izquierda.
2. Pulsa el botón **Tradurre →** (o `Ctrl+Enter`).
3. La traducción en italiano aparece en el área derecha.

### Ejemplos rápidos (botones del profesor)

- *Me gusta el fútbol*
- *¿Cómo estás?*
- *¿Qué hora es?*

## Endpoints del backend

| Método | Ruta         | Descripción                          |
|--------|--------------|--------------------------------------|
| GET    | `/health`    | Verifica que el servidor y el modelo estén listos |
| POST   | `/translate` | Traduce texto ES → IT                |

### Ejemplo de llamada a `/translate`

```bash
curl -X POST http://localhost:5000/translate \
     -H "Content-Type: application/json" \
     -d '{"text": "Buenos días"}'
```

Respuesta:
```json
{"translation": "Buongiorno"}
```

## Notas técnicas

- El modelo se carga **una sola vez** al arrancar para minimizar latencia.
- Se usa un **prompt few-shot** ya que Qwen2-0.5B es el modelo base (no Instruct), lo que guía al modelo a completar la traducción.
- La inferencia corre en CPU por defecto; si tienes GPU compatible con CUDA se usará automáticamente gracias a `device_map="auto"`.
- Tiempo de respuesta aproximado: 5-20 segundos en CPU, 1-3 segundos en GPU.
