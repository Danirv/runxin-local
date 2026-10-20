[English](protocol.md) | [Català](protocol.ca.md) | [Español](protocol.es.md) · [Documentación](index.md)

<a id="capas-del-protocolo-y-evidencia"></a>
<a id="trama-y-códecs-f79d"></a>
<a id="semántica-de-las-escrituras"></a>
<a id="superficie-home-assistant"></a>
<a id="agua-estadísticas-y-sal"></a>
<a id="campo-52"></a>
<a id="transporte-bl3372"></a>
<a id="límite-de-compatibilidad"></a>

# Tramas del protocolo y entrega

Home Assistant aplica la política del controlador; el cliente F79D construye y valida tramas Runxin crudas; el transporte añade su envoltorio y gestiona la sesión. La [arquitectura](architecture.es.md) concreta las responsabilidades.

## Trama F79D

La trama exterior observada empieza `5A 5C` y acaba `A5`; la interior empieza `DF FD` y acaba `DE`. Ambas tienen checksum aditivo de 8 bits. Los campos son triples `[field_id, byte_1, byte_2]`.

| Operación | Petición | Respuesta |
|---|---|---|
| Lectura | `0x09` | `0xC9` |
| Escritura | `0x19` | `0xD9` |

No existe una endianidad global. El [catálogo F79D](f79d.es.md) define códecs, volúmenes emparejados y unidades. El campo 7 es BE en el G6 probado pese a la interpretación distinta de la app antigua; la [evidencia física](hardware-verification.es.md#evidencia-del-campo-7) explica el motivo. La [matriz](model-support.md) concreta conversiones y permisos por modelo.

## Modelo de evidencia

| Etiqueta | Significado |
|---|---|
| `legacy_app_codec` | Representación recuperada de la app |
| `device_state_observed` | Valor/comportamiento observado en el controlador |
| `hardware_write_verified` | Orden local, lectura independiente nueva y confirmación física/semántica |
| `cloud_write_observed` | Cambio observado por la vía del fabricante |
| `inferred` | Interpretación no confirmada independientemente |

Las etiquetas no conceden permisos de escritura. Un ACK no es evidencia física. La [verificación](hardware-verification.es.md) registra procedimiento y resultados por modelo; la [investigación WaterDevice](waterdevice-audit.es.md) distingue el comportamiento antiguo de la aceptación en el firmware probado.

## Entrega de lecturas y escrituras

Las lecturas son idempotentes y pueden tener reintentos acotados. Las escrituras se envían una vez: timeout, respuesta perdida o error después del envío dejan un resultado ambiguo. El coordinador hace un GET nuevo y reconcilia sin repetir la orden a ciegas. Una acción mecánica también exige la transición de fase esperada.

La caché no confirma un ajuste. El [transporte BL3372](broadlink-bl3372.es.md) describe autenticación, validación, cierre y reintentos. El prefijo LE de dos bytes, cifrado y comando BroadLink `0x6A` quedan fuera del contrato Runxin crudo.

## Política HA y capacidad del códec

El códec sabe codificar más campos de los que HA expone. `write_fields` solo permite ajustes reversibles autorizados con validación de rango/unidad; el campo mecánico 34 se gestiona por separado. El campo 49 se lee/codifica para investigación, pero no tiene escritor HA porque el SET local directo no se confirmó en el G6 probado.

La [guía de uso](usage.es.md) concentra estadísticas, sal y vacaciones. El bloque 1–51 y la caché separada del campo 52 son política del adaptador, no un límite universal. Un controlador o transporte nuevo necesita [evidencia de perfil](adding-a-device-profile.es.md), no una suposición basada en marca o módulo.
