# Alcance comercial del editor ISH

Este documento separa las funcionalidades de la cotizacion
`COT-2026-017` del desarrollo adicional de un sitio web personalizado. No
reemplaza la cotizacion; sirve como referencia tecnica para evitar mezclar los
dos alcances.

## Cotizacion COT-2026-017 - $800.000 liquido

El modo predeterminado del editor corresponde a este alcance.

| Etapa | Entregable cotizado | Implementacion |
| --- | --- | --- |
| 01 | Levantamiento y auditoria | Inventario de paginas, secciones, colecciones y recursos en `content/` y `scripts/`. |
| 02 | Interfaz de administracion | Panel local con paginas existentes, contenido compartido, medios, historial, inspector y vista previa responsive. |
| 03 | Administracion y autenticacion | Usuario y contrasena locales, hash PBKDF2, cookie `HttpOnly`, sesiones en memoria y API FastAPI local. |
| 04 | Modulo de noticias | Crear, editar, publicar/despublicar, ordenar y eliminar comunicaciones; imagen opcional y texto enriquecido. |
| 05 | Contenidos existentes | Edicion de textos, enlaces e imagenes ya modelados, sin crear paginas o secciones. |
| 06 | Integracion | Generacion del sitio estatico, validacion y publicacion transaccional a `gh-pages`. |
| 07 | QA y seguridad | Sanitizacion, validacion de rutas/medios, control de acceso, pruebas automatizadas y comprobaciones responsive. |
| 08 | Despliegue y capacitacion | Lanzadores, especificacion de paquetes, manual de usuario y arquitectura. La capacitacion y garantia son actividades de entrega. |

Tambien se consideran parte de la calidad operativa del panel base el guardado
automatico, deshacer/rehacer, vista previa responsive, biblioteca de medios,
historial de borradores y validacion previa a publicar. Estas funciones apoyan
los entregables cotizados y no crean nuevas superficies del sitio publico.

La autenticacion del editor no usa ningun servicio en linea. GitHub interviene
solamente cuando el usuario elige **Sincronizar** o **Publicar**. Los borradores,
la edicion, los medios locales y la vista previa funcionan sin conexion.

## Sitio personalizado - $1.200.000 liquido

Las siguientes capacidades pertenecen al alcance adicional indicado como
"Desarrollar un sitio web personalizado con edicion de cada pagina, creacion de
nuevas paginas y plantillas":

- Crear y eliminar paginas.
- Definir rutas y modificar la navegacion.
- Crear secciones desde plantillas.
- Duplicar, eliminar, ocultar y reordenar secciones.
- Cambiar variantes estructurales y composicion de las paginas.
- Agregar, eliminar o reordenar colecciones distintas del modulo de noticias.
- Ampliar el catalogo de plantillas de pagina y sus opciones de diseno.
- Crear nuevos tipos de contenido, campos, bloques o colecciones compartidas.
- Alterar encabezados, pies, menus, jerarquias o estructura responsive.
- Incorporar variantes de layout, estilos visuales o un rediseno.
- Agregar formularios, buscador, idiomas, agenda, filtros u otra funcionalidad
  publica que no exista en el sitio actual.
- Integrar nuevos servicios externos, migraciones o importaciones masivas.

La regla de clasificacion es simple: editar el valor de un texto, enlace o
imagen existente pertenece al modo base; crear, eliminar o reorganizar la
estructura que lo contiene pertenece al sitio personalizado. La unica excepcion
es **Comunicaciones**, porque su alta, baja, orden y publicacion forman parte
explicita del modulo de noticias cotizado.

El modo personalizado implementado incluye actualmente plantillas de pagina,
catalogo de secciones, altas y bajas, duplicacion, visibilidad, orden,
navegacion y edicion de rutas. Una solicitud futura de nueva funcionalidad se
registra en esta categoria y se revisa contra el alcance aceptado antes de
incorporarla.

### Clasificacion de la actualizacion ICH2026 de agosto de 2026

Para esta entrega, la separacion practica queda documentada asi:

- **Modo basico:** actualizar fechas, tarifas y textos existentes; publicar las
  novedades de ICH2026 y del Vaccine Working Group en Comunicaciones; y mantener
  los formularios de fellowships y nominaciones como enlaces externos de Google
  Forms. El editor no recibe, almacena ni administra respuestas de formularios.
- **Modo avanzado:** crear la pagina `/awards/`, incorporarla a la navegacion,
  agregar la coleccion compartida de premios anteriores y sumar las plantillas
  estructurales para oportunidades, perfiles de premios y archivo historico.

Esta clasificacion permite retirar la distincion comercial mediante la edicion
`unified` sin cambiar los contenidos ni mantener dos versiones del sitio.

## Ediciones de entrega

La misma aplicacion se entrega en tres configuraciones. La seleccion queda
guardada localmente y no requiere mantener ramas ni versiones distintas:

| Edicion | Interfaz | Funciones estructurales |
| --- | --- | --- |
| `basic` | Muestra **Edicion Basica · $800.000 liquido** y explica que paginas, secciones y plantillas corresponden al alcance avanzado. | Desactivadas. |
| `advanced` | Muestra **Edicion Avanzada · $1.200.000 liquido** y la comparacion de alcances. | Activadas. |
| `unified` | No muestra precios, nombres de edicion ni comparacion comercial. | Activadas como parte integral del producto. |

Para seleccionar la entrega se ejecuta una vez:

```bash
./start-editor.sh --edition basic
./start-editor.sh --edition advanced
./start-editor.sh --edition unified
```

En Windows se usan los mismos argumentos con `start-editor.cmd`. Las aperturas
posteriores recuerdan la seleccion. `ISH_EDITOR_EDITION` puede definirla sin
persistencia en automatizaciones y `ISH_EDITOR_SCOPE=custom` se conserva como
alias compatible de `advanced`.

La opcion `unified` es la entrega recomendada cuando el cliente contrata el
desarrollo de $1.200.000 y se desea presentar todas las herramientas como un
solo paquete, sin distincion comercial dentro del editor.

## Fuera de ambos totales

La mantencion mensual de `$50.000` liquidos se factura por separado, tal como
indica la cotizacion. Servicios externos, hosting de un panel en linea,
autenticacion remota y operacion multiusuario no forman parte del editor local.
Un panel alojado en internet, roles y permisos por persona, inicio de sesion con
Google/GitHub/SSO o trabajo simultaneo requieren una cotizacion independiente,
porque contradicen el requisito actual de acceso exclusivamente local.
