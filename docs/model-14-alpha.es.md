# Modelo 14 / Runxin F136: soporte Midnight Alpha

[English](model-14-alpha.md) | [Català](model-14-alpha.ca.md) | [Español](model-14-alpha.es.md)

Runxin Local **2.9.0** admite el modelo **14 / F136** con BL3372 (`0x520F`) y el protocolo compatible F79D existente. La release es estable; **Alpha** describe el soporte de este controlador, inicialmente el Euro-Clear Midnight 25 / ECOPRO+ de la [issue #22](https://github.com/Danirv/runxin-local/issues/22).

El usuario añadió el modelo localmente y declara que funcionan descubrimiento, autenticación, lecturas y el mapa del modelo 12. Aceptamos como evidencia aportada las escrituras que declara verificadas: **4 (reloj), 6 (límite de tiempo de caudal), 10 (hora de regeneración) y 43 (sal añadida)**. **7 (umbral de caudal), 34 (acciones mecánicas) y 47 (dureza)** siguen pendientes.

Instala 2.9.0 o posterior, reinicia HA y añade Runxin Local. No es necesario editar el registro. Una entrada operativa que ya funcionaba con la modificación local puede actualizarse conservando dominio e identificadores MAC; revisa otras modificaciones locales antes de sustituir la carpeta. Una entrada solo de diagnóstico no se transforma: descarga su informe y elimínala antes de añadir el dispositivo operativo.

Se ofrecen los sensores y controles Midnight, incluida la corrección automática del reloj, los ajustes, el botón de regeneración y los servicios validados. Se mantienen codificaciones, rangos, comprobaciones de estado y lectura posterior estricta. Los controles pendientes siguen disponibles para validación; vacaciones sigue siendo de solo lectura.

La resina utiliza **primer byte crudo × 0,1 L**, como el modelo 12, a partir del mapa compartido declarado. Falta la comparación directa entre bytes del modelo 14 y pantalla/app: el sensor y los diagnósticos muestran `resin_volume_scale_confirmed=false` y conservan ambos bytes. Los enums desconocidos siguen visibles.

Son útiles los diagnósticos guardados de HA, la entrada exacta añadida y los valores/unidades de resina y otras lecturas de la app o pantalla. No es necesario repetir pruebas completadas; pueden aportarse los resultados iniciales/cambio/lectura/restauración disponibles. No hay que iniciar una acción mecánica solo para elaborar el informe. [Verificación física](hardware-verification.es.md).
