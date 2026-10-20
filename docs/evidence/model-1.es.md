# Modelo 1 / F150: registro de evidencia

Observaciones fechadas, valores reportados y límites. La [guía actual](../models/model-1.es.md) describe alta y controles. Este registro no es una petición de nuevas pruebas.

[English](model-1.md) | [Català](model-1.ca.md) | [Español](model-1.es.md) · [Documentación](../index.md)

## Confirmaciones incorporadas en 2.9.3

La [respuesta del 10-10-2026](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6096161743) confirma reloj inicial 11:23, escrituras a 11:24 y 11:26 y restauración con el botón de sincronización manual. La pantalla del controlador y Water Device coinciden tras cada acción. Solo se probó el campo 4 y después se desactivó la opción experimental. No valida la corrección automática ni otras escrituras.

La pantalla física está en neerlandés con código de idioma 7. HA corrige únicamente esa correspondencia del modelo 1, sin escribir el idioma ni cambiar el de la app; los demás códigos conservan las etiquetas de referencia.

El equipo tiene 24 L nominales de resina, pero el campo 26 sigue `F0 00` (referencia 240) y los campos 41–42 siguen en 15. En el frontend del fabricante, `resinVolume` es Resin volume y `periodicWaterProduction` es Water treatment capacity. No hemos confirmado independientemente qué campo local modificaba esa pantalla de la antigua app Runxin. `240 / 10 = 24 L` es plausible, pero aún no es una comparación con el valor configurado. Se conservan ambas lecturas sin unidad asumida y no se aplica el códec U16 del modelo 14.

El volumen de resina debe describir la carga real, no adaptarse al número de personas. La capacidad de tratamiento es otro parámetro que depende de resina, dureza y ajustes de regeneración; reducirla manteniendo los ciclos puede hacer regenerar más a menudo en lugar de ahorrar. Hay que aclarar etiqueta/unidad y seguir las instrucciones del equipo antes de proponer un cambio. No hace falta volver a emparejar, recuperar la app antigua, repetir diagnósticos ni modificar ajustes para aclarar las lecturas.


## Funcionamiento reportado después de regenerar con 2.9.3

La [respuesta posterior del 10-10-2026](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6101162421) confirma consultas periódicas normales y recuperación de las lecturas tras reiniciar HA después de las actualizaciones. La unidad reporta modelo 1, firmware BL3372 62016 e integración 2.9.3.

A las 19:41:45, hora local, HA mostraba aspiración de salmuera y enjuague lento mientras el controlador indicaba **“pekel-spoel traag up-flow”**. Esto contrasta esa fase concreta. HA había indicado llenado de salmuera a las 19:35:34, unos seis minutos antes. Con consultas cada 60 segundos, esta observación no valida independientemente la duración configurada ni demuestra un error respecto a los siete minutos de la lectura anterior. Los intentos abortados anteriores se excluyen de la validación de secuencia y duraciones. La opción de regeneración de HA permaneció desactivada: no valida la orden de inicio del campo 34.

Después del ciclo, HA mostraba capacidad restante **3429 L**, frente a los **1267 L** reportados el 8 de octubre. Se registra una recuperación de capacidad tras regenerar, sin calibración independiente de la unidad. Se mantienen dureza 280 mg/L, resina `F0 00` / referencia 240 y referencia por ciclo 15. Suponiendo dureza expresada como CaCO₃, `3,429 m³ × 28 °f ≈ 96 °f·m³`, unos `4 °f·m³/L` para los 24 L nominales de resina. Es una comprobación de coherencia, no una comparación con la resina configurada ni una prueba de la escala 0,1. El usuario recuerda una etiqueta L junto al ajuste antiguo, pero no está seguro; la unidad y correspondencia exacta con el campo local siguen pendientes.

Se incorpora evidencia de funcionamiento y de una fase, sin cambiar códecs ni permisos; la posterior 2.10.2 promueve lecturas a Beta manteniendo las dos unidades pendientes. Las comparaciones anteriores son puntos de calibración pendientes: no se piden más pruebas, capturas ni diagnósticos a este contribuyente. La incidencia original de conexión/alta puede cerrarse independientemente de estas validaciones.
