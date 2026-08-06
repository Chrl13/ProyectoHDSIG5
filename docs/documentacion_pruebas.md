# Documentación de Pruebas de Software

## 1. Introducción

Este documento describe la estrategia de pruebas implementada para el proyecto backend desarrollado con **Python utilizando Flask 3.x**, Flask-SQLAlchemy como ORM, SQLite como base de datos, Authlib para autenticación OAuth2 con Auth0 y Jinja2 para la generación de vistas.

El objetivo de esta implementación es validar la calidad y estabilidad del sistema mediante diferentes tipos de pruebas de software:

* Pruebas unitarias.
* Pruebas de integración.
* Pruebas funcionales.

Para la ejecución de las pruebas se utilizaron herramientas del ecosistema Python:

* **PyTest**: Framework principal para la ejecución de pruebas.
* **pytest-cov**: Herramienta para medir cobertura del código.
* **Selenium WebDriver**: Automatización de pruebas funcionales sobre la interfaz web.
* **requests-mock**: Simulación de respuestas externas durante las pruebas de integración.

---

# 2. Arquitectura de pruebas implementada

Las pruebas fueron organizadas separando cada tipo de validación:

```
tests/
│
├── unit/
│   ├── test_models.py
│   └── test_auth.py
│
├── integration/
│   ├── test_users_api.py
│   └── test_historial_api.py
│
└── functional/
    └── test_app_flow.py
```

Esta separación permite mantener una estructura clara y facilita la ejecución individual de cada grupo de pruebas.

---

# 3. CRUDs evaluados

Para las pruebas se seleccionaron los siguientes módulos del sistema:

## 3.1 Users

Operaciones evaluadas:

* Creación de usuarios mediante flujo de autenticación.
* Consulta de usuarios.
* Consulta de roles disponibles.
* Actualización del rol de un usuario.

Endpoints evaluados:

```
GET  /api/users
GET  /api/roles
PUT  /api/users/<id>/role
GET  /api/user/roles
```

Pruebas realizadas:

* Creación y persistencia de usuarios.
* Validación de roles.
* Control de permisos según nivel de acceso.
* Actualización correcta de información.

---

## 3.2 HistorialConsulta

Operaciones evaluadas:

* Registro de consultas climáticas.
* Consulta del historial almacenado.
* Validación de información meteorológica.

Endpoints evaluados:

```
GET /api/clima
GET /api/historial
GET /api/pronostico
```

Pruebas realizadas:

* Creación de registros de historial.
* Consulta de información almacenada.
* Validación de respuestas de la API externa utilizando mocks.

---

# 4. Tipos de pruebas implementadas

## 4.1 Pruebas unitarias

Cantidad total:

```
38 pruebas unitarias
```

Ubicación:

```
tests/unit/
```

### test_models.py

Cantidad:

```
23 pruebas
```

Objetivo:

Validar el comportamiento individual de los modelos del sistema.

Se verifican:

* Creación de modelos Role, User e HistorialConsulta.
* Relaciones entre entidades.
* Restricciones de base de datos.
* Representación de objetos.
* Inicialización de datos.
* Validaciones internas.

---

### test_auth.py

Cantidad:

```
15 pruebas
```

Objetivo:

Validar la lógica de autenticación y autorización.

Se verifican:

* Jerarquía de roles.
* Función `has_role()`.
* Decorador `login_required`.
* Decorador `role_required`.
* Restricciones de acceso según permisos.

---

# 4.2 Pruebas de integración

Cantidad total:

```
41 pruebas de integración
```

Ubicación:

```
tests/integration/
```

Estas pruebas validan la comunicación entre diferentes componentes del sistema:

* Flask.
* Base de datos.
* Modelos.
* Endpoints REST.
* Servicios externos simulados.

---

## test_users_api.py

Cantidad:

```
21 pruebas
```

Validaciones:

* Consulta de usuarios.
* Consulta de roles.
* Actualización de roles.
* Permisos de usuarios.
* Respuestas HTTP.
* Manejo de errores.

Herramienta utilizada:

```
Flask Test Client
```

---

## test_historial_api.py

Cantidad:

```
20 pruebas
```

Validaciones:

* Registro de consultas climáticas.
* Consulta del historial.
* Pronóstico meteorológico.
* Respuestas correctas de API.
* Simulación de servicios externos mediante mocks.

Herramienta utilizada:

```
requests-mock
```

---

# 4.3 Pruebas funcionales

Cantidad total:

```
12 pruebas funcionales
```

Ubicación:

```
tests/functional/
```

Herramienta utilizada:

```
Selenium WebDriver
```

Estas pruebas validan el comportamiento completo del sistema desde la perspectiva del usuario.

Se verifican:

* Carga inicial de la aplicación.
* Navegación entre páginas.
* Redirecciones de rutas protegidas hacia el inicio de sesión.
* Inicio de sesión.
* Manejo de cookies.
* Control de acceso basado en roles (RBAC).
* Cierre de sesión.

Las pruebas de redirección se agruparon en un único caso de prueba que recorre las seis rutas protegidas (`/dashboard`, `/dashboard/clima`, `/dashboard/clima/historial`, `/dashboard/usuarios`, `/dashboard/clima/pronostico`, `/dashboard/config`) y valida que todas devuelvan una redirección (302) hacia `/login`, evitando capturas repetitivas de la misma página de inicio de sesión.

---

# 5. Resultado de ejecución

Ejecución completa:

```
91 pruebas ejecutadas
91 pruebas aprobadas
0 pruebas fallidas
```

Tiempo total:

```
105.33 segundos
```

Detalle:

| Tipo de prueba | Cantidad | Resultado |
| -------------- | -------: | --------- |
| Unitarias      |       38 | PASS      |
| Integración    |       41 | PASS      |
| Funcionales    |       12 | PASS      |
| Total          |       91 | PASS      |

---

# 6. Comandos para ejecutar pruebas

## Ejecutar todas las pruebas

```bash
.venv\Scripts\python -m pytest tests/ -v
```

Resultado esperado:

```
91 passed
```

---

## Ejecutar únicamente pruebas unitarias

```bash
.venv\Scripts\python -m pytest tests/unit/ -v
```

Resultado esperado:

```
38 passed
```

---

## Ejecutar pruebas de integración

```bash
.venv\Scripts\python -m pytest tests/integration/ -v
```

Resultado esperado:

```
41 passed
```

---

## Ejecutar pruebas funcionales con Selenium

Requiere Google Chrome instalado.

```bash
.venv\Scripts\python -m pytest tests/functional/ -v
```

Resultado esperado:

```
12 passed
```

---

# 7. Reportes y evidencias generadas

Al ejecutar la suite completa se generan automáticamente:

```
reports/
│
├── report.html
│
├── coverage/
│   ├── index.html
│   ├── app_py.html
│   └── models_py.html
│
└── screenshots/
```

---

## Reporte HTML de pruebas

Archivo:

```
reports/report.html
```

Contiene:

* Lista completa de pruebas ejecutadas.
* Estado de cada prueba.
* Tiempo de ejecución.
* Resultados obtenidos.

---

## Reporte de cobertura

Ubicación:

```
reports/coverage/index.html
```

Cobertura obtenida:

```
84%
```

Detalle:

| Archivo   | Cobertura |
| --------- | --------: |
| app.py    |       82% |
| models.py |      100% |
| Total     |       84% |

La cobertura permite identificar qué partes del código fueron ejecutadas durante las pruebas.

---

## Evidencia Selenium

Ubicación:

```
reports/screenshots/
```

Cantidad generada:

```
31 capturas PNG
```

Las capturas documentan las páginas reales que el navegador muestra en cada caso de prueba, por lo que cada imagen representa el resultado efectivo de la prueba (página de inicio, dashboard, gestión de usuarios, acceso denegado, clima o cierre de sesión).

Ejemplo de nomenclatura:

```
TestHomePage__test_home_page_loads__02_pagina_cargada.png

TestAuthenticatedPages__test_dashboard_loads_when_authenticated__03_dashboard_cargado.png

TestAuthenticatedPages__test_usuarios_page_forbidden_for_viewer__03_acceso_denegado_viewer.png
```

---

# 8. Conclusión

La implementación de pruebas permite verificar la estabilidad del sistema mediante diferentes niveles de validación.

Se logró implementar:

* 38 pruebas unitarias para validar componentes individuales.
* 41 pruebas de integración para validar comunicación entre módulos.
* 12 pruebas funcionales utilizando Selenium para validar flujos completos del usuario.

La ejecución final obtuvo:

```
91/91 pruebas aprobadas
```

demostrando que las funcionalidades evaluadas trabajan correctamente bajo los escenarios definidos.