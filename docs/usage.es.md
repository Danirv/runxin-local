# Utilizar Runxin Local

[English](usage.md) | [Català](usage.ca.md) | [Español](usage.es.md) · [Documentación](index.md)

## Entidades y controles

Las entidades operativas muestran caudal, consumo diario, capacidad restante, estado, modo de regeneración, patrón de trabajo, vacaciones y avisos activos. En Diagnóstico están duraciones/cuentas atrás, recordatorios, resina, identidad y comunicación. Algunas entidades están deshabilitadas por defecto; actívalas en la lista de entidades del dispositivo si las necesitas.

Los controles dependen del [modelo](model-support.md). Los modelos 9/12/14 conservan reloj, hora de regeneración, dureza, sal añadida, protecciones, botón de regeneración y servicios administrativos; las validaciones pendientes se documentan separadamente de los permisos. El modelo 1 solo ofrece reloj manual validado por defecto, con opciones explícitas para otras pruebas. [Guía](models/model-1.es.md).

Un dato ausente no se convierte en cero. Los enums desconocidos muestran el código decimal y `raw_code`; las etiquetas conocidas siguen el mapa de referencia y las excepciones confirmadas por modelo.

## Consumo de agua y estadísticas

| Entidad | Significado | Estadísticas HA |
|---|---|---|
| Consumo diario | Contador acumulado del día; se reinicia al cambiar de día | `total_increasing`; fuente de agua del panel de Energía |
| Caudal | Última muestra instantánea | `measurement`; puede omitir consumos cortos entre consultas |
| Capacidad de tratamiento restante | Cantidad restante del controlador, no agua almacenada | `measurement` |
| Consumo semanal medio del controlador | Media informada por el controlador, no el total histórico de la app | Sin clase estadística |
| Capacidad de tratamiento por ciclo | Cantidad del ciclo de tratamiento, no agua consumida | Sin clase estadística |

Después del alta o de actualizar el modelo 1, espera a que HA recoja estadísticas y selecciona **Consumo diario** como fuente de agua en Energía. Conserva las entidades existentes. No se recuperan retroactivamente estadísticas a largo plazo que nunca se generaron.

Para obtener el consumo de la semana, derívalo del contador diario/historial. Si HA ofrece eliminar estadísticas antiguas de la media semanal o capacidad por ciclo, esa limpieza no elimina las entidades ni el historial normal del Recorder.

Las unidades siguen el selector del controlador. Resina y capacidad por ciclo del modelo 1 siguen **sin unidad**, multiplicador supuesto ni estadísticas. Los modelos 12 y 14 usan códecs de bytes distintos para la resina; consulta la [política](model-support.md).

## Sal, resina y mantenimiento

**Cantidad de sal añadida** es el ajuste 43 del controlador (0–100 kg), no un nivel físico del depósito. La integración escribe el valor solicitado: enviar dos veces 25 kg no implementa un acumulador de 50 kg en HA. No estima ni descuenta sal después de regenerar. Concentración baja de salmuera y recordatorio de sal son señales separadas.

El volumen de resina es un parámetro configurado, no una medida del contenido físico. La capacidad nominal puede diferir del valor configurado. El umbral de regeneraciones para el recordatorio de resina no es el recuento de ciclos realizados.

## Opciones de consulta y reloj

En **Configurar**, el intervalo normal es de **60 segundos** y el adaptativo de **10 segundos** con caudal o transición mecánica observada. En los modelos 9/12/14, el sondeo adaptativo y la corrección automática del reloj están activados por defecto. La tolerancia del reloj es de **2 minutos**; el cambio estacional puede provocar una corrección.

El modelo 1 empieza con 60 segundos fijos y sondeo adaptativo desactivado. El reloj automático queda bloqueado independientemente de la opción guardada; reloj y sincronización manuales siguen disponibles. Los ajustes experimentales y el inicio de regeneración son opciones separadas desactivadas por defecto.

El campo 52 se refresca independientemente cada **3600 segundos** y se guarda en caché. Los bytes de los diagnósticos pueden tener distinta antigüedad; no todos los campos se han consultado necesariamente juntos.

## Vacaciones y regeneración

Vacaciones es solo lectura: `off` si el flag es falso; `preparing` si es verdadero antes de alcanzar la estación estable 8; `active` si es verdadero y la estación es 8. El estado operativo crudo se conserva. Vacaciones estable no mantiene la consulta rápida.

El botón de regeneración exige una lectura nueva en servicio con vacaciones desactivadas, rechaza peticiones simultáneas, envía una orden y comprueba la fase resultante. Mueve la válvula y utiliza agua/sal. Un ACK no prueba un cambio; los resultados ambiguos se contrastan con lecturas nuevas sin repetir la orden a ciegas. La [verificación física](hardware-verification.es.md) concreta qué se ha probado por modelo.

## Servicios avanzados

**`ypsilon_local.write_fields`** es administrativo y admite ajustes reversibles permitidos, con validación de valor crudo, rango y unidad. **`ypsilon_local.advance_phase`** gestiona por separado el avance de fases. Ambos aplican los permisos efectivos; las entradas de diagnóstico no pueden escribir. El modelo 1 no permite avanzar fases y el campo 49 no tiene escritor HA.

Para el uso habitual, utiliza los controles de entidad. La capacidad del códec es más amplia que los permisos HA; consulta el [catálogo](f79d.es.md) para interpretar valores crudos.

## Diagnósticos y ayuda

**Descargar diagnósticos** de una entrada operativa exporta datos en caché sin iniciar otra consulta. El [informe de compatibilidad](compatibility-report.md) hace lecturas puntuales explícitas y acotadas; la entrada guardada no tiene entidades, consultas periódicas ni controles. Para errores de conexión, consulta la [guía](troubleshooting.es.md).
