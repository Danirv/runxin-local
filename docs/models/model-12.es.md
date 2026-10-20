# Modelo 12 / F105: Euro-Clear Midnight

[English](model-12.md) | [Català](model-12.ca.md) | [Español](model-12.es.md) · [Matriz de soporte](../model-support.md) · [Documentación](../index.md)

**Beta**, limitado al Euro-Clear Midnight 25 probado con cabezal ECOPRO+ y BL3372 `0x520F`, que devuelve código de controlador 12. F105 es el nombre del enum de la API; no equivale a cualquier referencia comercial de válvula.

## Alta y controles

Sigue la [instalación y actualización](../installation.es.md) y conserva las entradas operativas. Hay lecturas/estadísticas normales, reloj, hora de regeneración, dureza, sal añadida, protección de caudal continuo y los controles de regeneración/servicios existentes. El reloj automático sigue las opciones normales. Vacaciones es solo lectura.

| Evidencia de escritura | Campos |
|---|---|
| Verificados físicamente en el equipo reportado | 4 reloj, 6 tiempo de caudal continuo, 10 hora de regeneración, 43 sal añadida |
| Pendientes de verificación, con permisos existentes conservados | 7 umbral de caudal, 47 dureza, 34 regeneración/acciones mecánicas |

Lecturas coincidentes no validan escrituras. Se mantienen rangos, unidades, política por modelo y reconciliación con lectura nueva. Beta no modifica permisos ni representa pruebas físicas nuevas.

## Resina, enums y dureza

El campo 26 `FA 00` conserva **U8 × 0,1** y muestra **25 L** en el Midnight 25 probado. Se guardan ambos bytes; esta captura no determina el significado del segundo. No debe copiarse el códec U16 del modelo 14. La resina es un parámetro configurado, no una medida del contenido físico.

El patrón de trabajo **255** y modo de relé **2** aparecen como decimales con `raw_code`; los manuales consultados no demuestran sus etiquetas de protocolo. Los datos ausentes siguen desconocidos.

El manual Midnight utiliza una convención de dureza propia (grados alemanes × 10, con una referencia CaO mg/L en otra página). Conserva el valor reportado y compara las unidades exactas del controlador/manual; no sustituyas silenciosamente la escala ni la generalices al G6.

## Evidencia

El [registro físico](../hardware-verification.es.md#euro-clear-midnight--modelo-de-controlador-12) recoge lecturas, cambios/restauraciones, sincronización del reloj, manuales y puntos pendientes. Si la app no funciona con el equipo, la pantalla del controlador puede aportar el contraste independiente. Las escrituras opcionales futuras se documentan por separado de las lecturas.
