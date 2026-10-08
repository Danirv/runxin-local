# Controlador modelo 1 / F150: Alpha de solo lectura

[English](model-1-alpha.md) | [Català](model-1-alpha.ca.md) | [Español](model-1-alpha.es.md)

**2.9.0** admite el código **1** con sensores de lectura periódica. El fabricante llama a este código **F150**, pero la identidad comercial del equipo de la issue #17 no está confirmada. No es soporte general para cualquier producto F150.

La release de la integración es estable; Alpha describe solo el soporte de este modelo.

1. Instala la versión 2.9.0 o posterior con HACS, o descarga el ZIP de la release y copia solo `custom_components/ypsilon_local` a `/config/custom_components/ypsilon_local`. Conserva una copia de la carpeta anterior y reinicia HA. Esta Alpha conserva el dominio; no requiere migrar a `runxin_local`.
2. Si existe una entrada exclusivamente de diagnóstico del mismo dispositivo, descarga primero su informe y elimina esa entrada antes de añadir el equipo normalmente.
3. Añade **Runxin Local**, introduce la IP y acepta la explicación **Alpha de solo lectura**. Consulta cada minuto por defecto, sin cadencia adaptativa. La corrección del reloj queda bloqueada aunque una opción antigua esté activada.
4. Compara los sensores con la app. Puedes habilitar las entidades de diagnóstico que estén desactivadas por defecto. No cambies ajustes para tomar capturas.
5. Descarga los diagnósticos desde el menú de la entrada y adjunta el JSON a la issue existente con algunos valores/capturas, unidades y hora aproximada. La descarga exporta el estado guardado y no inicia otra exploración. Oculta identificadores en las capturas.

No hay controles **number, time o button**, ni ajustes de reloj, configuración o acciones mecánicas. Los servicios administrativos también rechazan escrituras. La política se aplica en el coordinador y el adaptador del cliente, independientemente de la interfaz; no existe una opción para habilitar escrituras en este modelo.

Todas las lecturas usan interpretaciones **F79D de referencia pendientes de validación con la app**. No generan estadísticas de largo plazo; el historial ordinario puede conservarse. Los atributos y diagnósticos incluyen los dos bytes recibidos por campo (`state._rawFieldBytes`), sin paquetes completos, claves ni sesiones. Recibir zero/false no demuestra aplicabilidad.

Comparaciones prioritarias:

| Campo | Referencia del informe | Pendiente |
|---|---|---|
| 26, resina | `F0 00`, primer byte 240 | HA muestra 240 sin L ni multiplicador asumido. Confirmar valor/unidad reales. |
| 41–42, cantidad por ciclo | 15 | Se muestra sin L. Confirmar nombre, significado y unidad. |
| 35–36, restante | 1304 L | Capacidad restante y unidad, cerca de la hora de lectura. |
| 37–40, diario/media semanal | 215 / 192 L | No confundir media del controlador con total histórico semanal. |
| 47, dureza | 280 mg/L | Etiqueta, valor y escala de dureza. |
| 43, sal añadida | 25 kg | Registro de sal añadida, no nivel físico. |
| 4/5/10 y 6/7/15/17/19/21/23 | Horas, protecciones y duraciones | Contrastar lo que exponga la app sin modificar ajustes. |

El segundo byte de resina se conserva sin deducir un códec U16. El campo 52 se guarda en una caché independiente y puede ser anterior al resto de la instantánea. Si app y HA interfieren, pausa la consulta o desactiva temporalmente la entrada; no hace falta volver a emparejar.

La [issue #17](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6044822202) confirma módulo `0x520F`, firmware 62016, autenticación con la app cerrada, código 1 estable y los 52 campos recibidos en dos consultas sin errores. Las tramas de prueba reconstruidas son sintéticas. No se han validado campos superiores al 52 ni escrituras; las futuras conversiones específicas no deben modificar G6/Midnight.
