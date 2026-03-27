# Tests de Carga con Locust

Este directorio contiene pruebas de carga usando [Locust](https://locust.io/) para validar el comportamiento de la infraestructura bajo estrés.

## Requisitos

- Python 3.8+
- pip

## Instalación

```bash
pip install locust
```

Verifica que se instaló correctamente:

```bash
locust --version
```

## Uso

### Modo Web UI (recomendado)

Ejecuta Locust con la interfaz web:

```bash
locust -f tests/locustfile.py
```

Abre tu navegador en `http://localhost:8089` y configura:

- **Number of users**: cantidad total de usuarios simulados
- **Spawn rate**: usuarios nuevos por segundo
- **Host**: la URL del ALB o servidor a probar (ejemplo: `http://mi-alb-123456.us-east-1.elb.amazonaws.com`)

### Modo headless (sin interfaz)

Para ejecutar directamente desde la terminal sin UI:

```bash
locust -f tests/locustfile.py --headless -u 100 -r 10 -t 60s --host http://<tu-host>
```

| Parámetro | Descripción |
|-----------|-------------|
| `-u 100`  | 100 usuarios concurrentes |
| `-r 10`   | 10 usuarios nuevos por segundo |
| `-t 60s`  | Duración total de la prueba |
| `--host`  | URL del servidor objetivo |

## Qué hace el test

`locustfile.py` simula usuarios que:

1. Hacen peticiones GET al endpoint `/`
2. Esperan entre 1 y 5 segundos entre cada petición

Esto permite validar que el Auto Scaling Group escale correctamente bajo carga.
