[English](protocol.md) | [Català](protocol.ca.md) | [Español](protocol.es.md) · [Documentació](index.md)

<a id="capes-del-protocol-i-evidència"></a>
<a id="trama-i-còdecs-f79d"></a>
<a id="semàntica-de-les-escriptures"></a>
<a id="superfície-home-assistant"></a>
<a id="aigua-estadístiques-i-sal"></a>
<a id="camp-52"></a>
<a id="transport-bl3372"></a>
<a id="límit-de-compatibilitat"></a>

# Trames del protocol i lliurament

Home Assistant aplica la política del controlador; el client F79D construeix i valida trames Runxin crues; el transport afegeix el seu embolcall i gestiona la sessió. L’[arquitectura](architecture.ca.md) concreta les responsabilitats.

## Trama F79D

La trama exterior observada comença `5A 5C` i acaba `A5`; la interior comença `DF FD` i acaba `DE`. Totes dues tenen checksum additiu de 8 bits. Els camps són triples `[field_id, byte_1, byte_2]`.

| Operació | Petició | Resposta |
|---|---|---|
| Lectura | `0x09` | `0xC9` |
| Escriptura | `0x19` | `0xD9` |

No hi ha una endianitat global. El [catàleg F79D](f79d.ca.md) defineix còdecs, volums aparellats i unitats. El camp 7 és BE al G6 provat malgrat la interpretació diferent de l’app antiga; l’[evidència física](hardware-verification.ca.md#evidència-del-camp-7) n’explica el motiu. La [matriu](model-support.md) concreta conversions i permisos per model.

## Model d’evidència

| Etiqueta | Significat |
|---|---|
| `legacy_app_codec` | Representació recuperada de l’app |
| `device_state_observed` | Valor/comportament observat al controlador |
| `hardware_write_verified` | Ordre local, lectura independent nova i confirmació física/semàntica |
| `cloud_write_observed` | Canvi observat per la via del fabricant |
| `inferred` | Interpretació no confirmada independentment |

Les etiquetes no concedeixen permisos d’escriptura. Un ACK no és evidència física. La [verificació](hardware-verification.ca.md) registra procediment i resultats per model; la [recerca WaterDevice](waterdevice-audit.ca.md) diferencia el comportament antic de l’acceptació al firmware provat.

## Lliurament de lectures i escriptures

Les lectures són idempotents i poden tenir reintents acotats. Les escriptures s’envien una vegada: timeout, resposta perduda o error després de l’enviament deixen un resultat ambigu. El coordinador fa un GET nou i reconcilia sense repetir l’ordre a cegues. Una acció mecànica també exigeix la transició de fase esperada.

La memòria cau no confirma un ajust. El [transport BL3372](broadlink-bl3372.ca.md) descriu autenticació, validació, tancament i reintents. El prefix LE de dos bytes, xifrat i comanda BroadLink `0x6A` queden fora del contracte Runxin cru.

## Política HA i capacitat del còdec

El còdec sap codificar més camps dels que HA exposa. `write_fields` només permet ajustos reversibles autoritzats amb validació de rang/unitat; el camp mecànic 34 es gestiona separadament. El camp 49 es llegeix/codifica per a recerca, però no té escriptor HA perquè el SET local directe no es va confirmar al G6 provat.

La [guia d’ús](usage.ca.md) concentra estadístiques, sal i vacances. El bloc 1–51 i la memòria cau separada del camp 52 són política de l’adaptador, no un límit universal. Un controlador o transport nou necessita [evidència de perfil](adding-a-device-profile.ca.md), no una suposició basada en marca o mòdul.
