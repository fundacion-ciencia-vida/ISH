# Guia de ISH Editor

ISH Editor permite mantener el sitio de la International Society for
Hantaviruses desde una interfaz visual local. Los borradores y la vista previa
funcionan sin internet. Solo **Sincronizar** y **Publicar** requieren conexion a
GitHub.

## 1. Acceso local

La primera apertura muestra un enlace de configuracion de un solo uso. Desde ese
enlace se define el usuario y una contrasena de al menos 10 caracteres. Las
credenciales quedan almacenadas mediante un hash en el perfil local del equipo;
no se envian a GitHub ni a otro servicio.

En las aperturas siguientes se usa la pantalla **Iniciar sesion**. La sesion se
cierra con el icono de salida de la barra superior, al detener el servidor local
o despues de 12 horas. El icono de llave permite cambiar la contrasena; las
otras sesiones locales se cierran al hacerlo. Cinco intentos fallidos bloquean
temporalmente nuevos intentos desde ese equipo.

Si se pierde la contrasena, se puede eliminar la configuracion local desde una
terminal y crear credenciales nuevas en la siguiente apertura:

```bash
./start-editor.sh --reset-auth
```

En Windows se usa `start-editor.cmd --reset-auth`. Este comando solo modifica el
perfil local y no cambia GitHub ni el contenido del sitio.

## 2. Instalar y abrir

La opcion recomendada es descargar el archivo correspondiente desde una release
del repositorio:

- Windows: `ISH-Editor.exe`.
- macOS: `ISH-Editor-macOS.dmg`.
- Linux: `ISH-Editor-x86_64.AppImage`.

Los paquetes aun no tienen firma comercial. Windows SmartScreen o macOS
Gatekeeper pueden mostrar una advertencia en la primera apertura. Verifique que
el archivo provenga del repositorio `fundacion-ciencia-vida/ISH`.

Git debe estar instalado y disponible en el equipo. Las aplicaciones incluyen
el editor, el servidor local y el generador del sitio; no requieren instalar
Python ni Node.js.

Para ejecutar desde el codigo fuente:

```bash
# Linux y macOS
./start-editor.sh
```

La entrega se selecciona una sola vez con `--edition basic`, `--edition
advanced` o `--edition unified`. La aplicacion recuerda la seleccion en este
equipo. `basic` muestra el alcance de $800.000; `advanced` habilita las
herramientas de $1.200.000 y mantiene visible la comparacion; `unified` habilita
todo sin mostrar nombres de plan ni precios.

En Windows, abra `start-editor.cmd`. La primera ejecucion requiere Python 3.11 o
superior, Node.js 20 o superior y conexion para instalar dependencias.

## 3. Conectar GitHub por primera vez

La aplicacion instalable solicita dos datos:

1. Un token personal de GitHub.
2. Una carpeta vacia donde guardar la copia local del sitio.

Para crear un token de alcance reducido en GitHub:

1. Abra `Settings > Developer settings > Personal access tokens > Fine-grained tokens`.
2. Limite el acceso al repositorio `fundacion-ciencia-vida/ISH`.
3. En `Repository permissions`, asigne `Contents: Read and write`.
4. Autorice el token para la organizacion si GitHub solicita SSO.

El token se guarda en el llavero seguro de Windows, macOS o Linux. No se escribe
en el repositorio, en los archivos de contenido ni en la direccion remota de
Git. Si el equipo no dispone de un llavero compatible, el acceso dura solamente
hasta cerrar la aplicacion.

Si se abre una copia existente que ya tiene un remoto SSH hacia
`fundacion-ciencia-vida/ISH`, el editor lo detecta y puede sincronizar y publicar
con la llave SSH del equipo, sin solicitar un token adicional.

## 4. Editar contenido

La barra izquierda separa el trabajo en cuatro areas:

- **Paginas**: elija una pagina y una seccion existente para modificar sus campos.
- **Compartido**: edite datos que aparecen en varios lugares, como fechas,
  navegacion, comites, reuniones, auspiciadores y enlaces.
- **Medios**: suba imagenes o PDF y seleccione recursos existentes.
- **Historial**: restaure un borrador local o una publicacion anterior.

La edicion basica no permite crear paginas ni secciones, modificar navegacion o
realizar cambios estructurales. Esas herramientas pertenecen al desarrollo de
sitio personalizado. Las ediciones `advanced` y `unified` incluyen plantillas
de pagina y seccion, rutas, navegacion, orden, visibilidad, duplicacion y
eliminacion estructural.

En **Comunicaciones** se pueden crear, eliminar y ordenar noticias. Cada registro
incluye el control **Publicada**, imagen opcional y contenido enriquecido. Una
noticia no publicada permanece en los datos, pero no aparece en el sitio.

El editor de texto admite negrita, cursiva, enlaces, listas, subtitulos, citas,
tablas y separadores. El HTML se filtra antes de guardarse para excluir scripts,
eventos y direcciones inseguras.

## 5. Imagenes y documentos

Una carga nueva permanece dentro del borrador hasta publicar. Las imagenes se
validan al subir y, durante la publicacion, se crean versiones WebP y AVIF en
varios tamanos. Los PDF deben contener una cabecera PDF valida.

Un recurso publicado solo se puede marcar para eliminacion cuando ya no aparece
en el contenido. La eliminacion del original y de todas sus variantes se aplica
al confirmar la siguiente publicacion.

## 6. Borradores y vista previa

Cada cambio se guarda automaticamente en `.ish-editor/`, una carpeta local que
Git ignora. La vista central se regenera despues de editar y permite revisar el
resultado en ancho de escritorio, tablet o movil.

**Deshacer** y **Rehacer** actuan durante la sesion actual. Antes de publicar se
crea ademas una revision persistente. El historial conserva hasta 50 revisiones
locales.

## 7. Publicar

1. Revise el sitio en los tres tamanos de vista previa.
2. Pulse **Sincronizar** para incorporar cambios recientes de GitHub.
3. Pulse **Publicar**.
4. Revise el resumen, escriba un mensaje breve y confirme.

La aplicacion crea una copia temporal, actualiza el contenido, procesa medios,
genera todas las paginas y ejecuta la validacion completa. Solo si todo termina
correctamente crea un commit y lo envia a `gh-pages`. GitHub Pages actualiza el
sitio publico desde esa rama.

## 8. Conflictos y recuperacion

La publicacion se detiene sin perder el borrador cuando ocurre cualquiera de
estas situaciones:

- Otra persona publico contenido despues de iniciar el borrador.
- La copia local contiene cambios manuales fuera del editor.
- GitHub y la copia local tienen historias divergentes.
- La generacion encuentra una ruta duplicada, un recurso faltante o HTML no valido.

En el primer caso, conserve el borrador, sincronice y vuelva a aplicar la edicion
sobre la version reciente. Para recuperar contenido, abra **Historial** y restaure
una revision; la version elegida vuelve como borrador y no se publica hasta que
usted confirme.

## 9. Alcance sin conexion

Sin internet se puede abrir una copia ya configurada, editar, subir archivos
locales, navegar la vista previa y consultar borradores. No se puede clonar por
primera vez, sincronizar ni publicar hasta recuperar la conexion.

El servidor escucha en `0.0.0.0` para poder abrirlo desde otro equipo autorizado
de la misma LAN o red Tailscale. Esto no convierte el editor en un servicio en
linea: el proceso, las credenciales y los datos siguen alojados en el equipo que
ejecuta la aplicacion.
