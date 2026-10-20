# Arquitectura

[English](architecture.md) | [Català](architecture.ca.md) | [Español](architecture.es.md) · [Documentación](index.md)

Runxin Local separa transporte, perfil de protocolo, política del controlador y presentación HA. **Modelo de controlador y perfil de protocolo son conceptos distintos**: varios modelos pueden compartir códec con unidades, permisos o campos aplicables diferentes.

| Capa | Responsabilidad |
|---|---|
| `transport/` | BroadLink, autenticación, cifrado, TFB, sockets y reintentos acotados; devuelve tramas sin interpretar campos. |
| `runxin/` | Framing, catálogo F79D, códecs, etiquetas y cliente de transacciones; independiente de HA/BroadLink. |
| `models.py` | Identidad, perfil, conversiones, incertidumbre, permisos efectivos y evidencia por modelo. |
| `api.py` | Composición F79D/BL3372, caché del campo 52 y tiempos; bloquea escrituras sin permiso antes del transporte. |
| `coordinator.py` | Consultas HA, estado obsoleto, cadencia y reconciliación; aplica la política también al reloj automático. |
| Entidades / servicios | Presentación y controles aplicables; no construyen paquetes. Ocultar controles no es la única protección. |
| Compatibilidad / informes | Exploración puntual acotada y almacenamiento local, separados de la consulta periódica. |

La estructura sirve para los modelos observados: reutilizar un mapa compatible y concentrar diferencias demostradas en la política del modelo. No copiar todo el catálogo por modelo.

`protocol_profile` identifica el camino `f79d` actual; **no es todavía una fábrica de códecs distintos**. El alta y el adaptador siguen usando F79D/BL3372. Un segundo protocolo local demostrado requerirá un descriptor/selector explícito de identidad, campos y códecs, conservando las fachadas actuales. No inventar códecs RO/F104 a partir de propiedades cloud. Un transporte nuevo debe implementar el contrato de trama cruda y habilitarse explícitamente para hardware probado.

Reglas:

- Recibir campos, validar significado/unidades y permitir escrituras son decisiones distintas. Los 52 campos no son un límite universal.
- Los modelos nuevos tienen `allowed_write_fields` vacío por defecto. El modelo 1 permite por defecto el campo 4 manual validado; las opciones de pruebas conceden permisos concretos al coordinador y al adaptador. El reloj automático y el campo 7 siguen bloqueados.
- G6/Midnight conservan controles y conversiones, con las acciones pendientes documentadas. Cambios específicos necesitan fixtures y regresiones para modelos existentes.
- Un ACK no demuestra estado físico; no hay reenvío ciego ante resultados ambiguos.
- Los códigos desconocidos y bytes originales se conservan; los campos ausentes no se inventan. Las lecturas provisionales no generan estadísticas a largo plazo.
- La consulta 1–51 y caché independiente del campo 52 se mantienen. Los datos pueden tener distinta antigüedad.
- Dominio `ypsilon_local`, config-entry v2, identidades MAC, unique IDs y fachadas se conservan. La migración de la PR #24 es un piloto separado.

El protocolo seguirá dentro del repositorio hasta que otro consumidor real justifique una biblioteca independiente. Consulta la [matriz de soporte](model-support.md), [guía del modelo 1](models/model-1.es.md).

La auditoría offline comprueba imports relativos anidados y dependencias del transporte. `write_policy` distingue evidencia del modelo y restricciones configuradas/del coordinador/adaptador con metadatos en caché. Consulta [CONTRIBUTING](../CONTRIBUTING.es.md) para los entornos de pruebas y la cobertura de CI.

El modelo 14 / F136 reutiliza el perfil y los controles Midnight, con las verificaciones aportadas en la issue #22 y los campos pendientes diferenciados. En 2.9.2, el modelo 14 es Beta: el campo 26 tiene una excepción de lectura U16 LE en `runxin/fields.py` y escala 0,1, confirmada con la pantalla. El cliente conserva la identidad validada para lecturas parciales, sin consultas adicionales. Los modelos 1 y 12 también tienen soporte Beta; permisos y puntos pendientes se definen por separado. Las conversiones G6/modelo 12 se mantienen. Consulta la [guía del modelo 14](models/model-14.es.md).

El modelo 1 tiene lecturas Beta desde 2.10.2, con estadísticas normales salvo resina/capacidad por ciclo sin unidad confirmada. Reloj y sincronización manuales (campo 4) están validados y no requieren opción experimental. Las opciones de pruebas conceden los campos 6/10/43/47; una segunda opción permite solo iniciar regeneración. Coordinador y adaptador aplican los permisos efectivos. Cambiarlos sustituye y revoca la sesión anterior sin perder la caché ni los sensores de referencia. El reloj automático, el campo 7 y el avance directo de fases siguen bloqueados.

## Ciclo de vida asíncrono

Las operaciones de red son asíncronas desde 2.10.0; 2.10.1 utiliza `broadlink-async>=1.1.0` y bloqueos `asyncio.Lock`. El autodiagnóstico cierra la sesión al cancelarse. Descargar la entrada cierra el socket; recargar crea un cliente nuevo conservando la caché del campo 52. El adaptador por dispositivo valida respuestas y evita reenvíos/reautenticación internos en escrituras, sin modificar clases globales. Las API internas quedan limitadas a la interfaz probada y cubiertas con AES real y UDP local simulado. Se requiere HA 2026.10.0+. [Migración](ha-2026-10.es.md).
