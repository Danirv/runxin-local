# Modelo 1 / F150

[English](model-1.md) | [Català](model-1.ca.md) | [Español](model-1.es.md) · [Matriz de soporte](../model-support.md) · [Documentación](../index.md)

**Lecturas Beta y reloj manual validado.** F150 es el nombre de la API del fabricante para el código 1, no una identidad comercial confirmada. La evidencia procede del equipo sin marca de la issue #17, BL3372 `0x520F`, firmware 62016; no valida todas las válvulas etiquetadas F150.

## Instalación

Sigue la [instalación y actualización](../installation.es.md). Conserva las entradas operativas; elimina una entrada solo de diagnóstico antes de dar de alta el mismo dispositivo. El alta explica las unidades pendientes. Por defecto consulta cada 60 segundos con sondeo adaptativo desactivado.

## Qué permite

- Lecturas normales de estado, agua y diagnóstico, con consumo diario `total_increasing` para Energía. La media semanal no es un contador acumulativo.
- **Reloj y sincronización manuales (campo 4)**, contrastados con app/controlador, sin opción experimental.
- Sensores de referencia, bytes recibidos y metadatos de permisos. Algunos diagnósticos están deshabilitados por defecto.
- **Resina y capacidad por ciclo sin unidad ni estadísticas.** `F0 00` / referencia 240 no determina litros ni multiplicador; la referencia 15 por ciclo es otro parámetro. Estas dos incertidumbres no bloquean las demás estadísticas.

Reloj automático, escrituras del umbral de caudal (7), vacaciones y avance directo de fases siguen bloqueados. El código de idioma 7 está confirmado como neerlandés en este modelo; otros enums mantienen interpretaciones de referencia.

## Ajustes experimentales opcionales

En **Ajustes → Dispositivos y servicios → Runxin Local → Configurar**, la opción de ajustes experimentales, desactivada por defecto, habilita los campos **6/10/43/47**: tiempo de caudal continuo, hora de regeneración, sal añadida y dureza. Las escrituras siguen pendientes de verificación física en el modelo 1.

Una segunda opción desactivada por defecto permite solo **iniciar regeneración (34)** y también requiere los ajustes experimentales. No permite avanzar fases arbitrariamente. Una futura validación física puede aprovechar un ciclo normalmente previsto; no es necesaria para obtener un informe.

En una prueba voluntaria reversible, parte de una lectura nueva, modifica un único valor permitido, compara lectura HA y app/controlador, restaura y comprueba la restauración. Una respuesta perdida no justifica repetir la orden a ciegas. Desactivar las pruebas revoca/reemplaza la sesión y elimina controles adicionales, conservando reloj manual, lecturas, identificadores y caché.

## Evidencia y puntos pendientes

El [registro fechado](../evidence/model-1.es.md) conserva valores crudos, restauración del reloj, idioma, fases y distinción entre resina y capacidad de tratamiento. La [verificación física](../hardware-verification.es.md) incluye los contrastes posteriores del consumo diario.

No se piden más pruebas ni informes al colaborador de la issue #17. La calibración pendiente es independiente de resolver aquella incidencia. Descargar diagnósticos de una entrada normal exporta el estado en caché, sin una exploración nueva.
