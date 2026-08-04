# Design System

## Direction

Interfaz de producto clara y contenida para trabajo editorial prolongado. Tema
claro, densidad media, superficies neutras y verde petroleo reservado para
seleccion, foco y acciones primarias.

## Typography

- Familia: Inter con fallback de sistema.
- Escala fija y compacta para paneles, formularios y barras de herramientas.
- Titulos internos pequenos; no usar tipografia de hero dentro del editor.

## Color

- Fondo de aplicacion: gris verdoso claro.
- Superficie: blanco suavemente tintado.
- Texto principal: carbon verdoso.
- Acento: verde petroleo.
- Informacion: azul medio.
- Advertencia: terracota.

Usar el acento solamente para seleccion, foco, estado activo y comandos
primarios. Los planes comerciales se distinguen por texto, icono y jerarquia,
no solamente por color.

## Components

- Radio maximo de 7 px; 5 px para botones, campos y filas.
- Iconos Lucide de 15 a 18 px.
- Botones de icono con tooltip y nombre accesible.
- Paneles separados por lineas de 1 px, sin tarjetas anidadas.
- Popovers breves para informacion contextual; modales solo para flujos que
  requieren confirmacion.

## Layout

- Barra superior fija.
- Riel de areas, lista lateral, vista previa y un inspector opcional.
- Los controles estructurales pertenecen a la edicion avanzada.
- En movil se conserva la edicion de listas e inspector; la vista previa queda
  disponible mediante tamanos dedicados en escritorio.

## Motion

Transiciones de estado entre 120 y 220 ms, sin rebote ni movimiento decorativo.
