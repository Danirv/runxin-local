# Arquitectura

[English](architecture.md) | [Català](architecture.ca.md) | [Español](architecture.es.md)

Runxin Local separa transport, perfil de protocol, política del controlador i presentació HA. **Un model de controlador no és un perfil de protocol**: diversos models poden compartir còdec i tenir unitats, permisos o camps aplicables diferents.

| Capa | Responsabilitat |
|---|---|
| `transport/` | BroadLink, autenticació, xifrat, TFB, sockets i reintents acotats. Retorna trames crues, sense interpretar camps. |
| `runxin/framing.py` | Embolcall observat, longituds, checksums i opcodes, independent de HA/BroadLink. |
| `runxin/fields.py`, `f79d.py`, `semantics.py` | Catàleg F79D, còdecs i etiquetes de referència. Els 52 camps no són un límit universal. |
| `runxin/client.py` | Transaccions serialitzades, resposta associada al tipus de petició i captura opcional de parells crus. |
| `models.py` | Identitat, perfil compartit, conversions, incertesa, permisos efectius i evidència per model. |
| `api.py` | Composició F79D/BL3372, memòria cau del camp 52 i temporització. Rebutja escriptures sense permís abans del transport. |
| `coordinator.py` | Lectures HA, dades antigues, cadència i reconciliació. Aplica la política també al rellotge automàtic. |
| Entitats / serveis | Presentació i controls aplicables; no construeixen paquets. Ocultar controls no és l'única protecció. |
| Compatibilitat / informes | Exploració puntual acotada, separada de la lectura periòdica. Les entrades de diagnòstic només carreguen l'informe desat. |

## Extensió

L'estructura actual és adequada per als models observats: reutilitzar el catàleg F79D compatible i concentrar particularitats demostrades a la política del model. No duplicar tot el protocol en fitxers per a cada model.

`protocol_profile` identifica el camí `f79d` compartit; encara **no és una fàbrica de còdecs diferents**. L'alta continua provant els camps d'identitat F79D i l'adaptador és específic de F79D/BL3372. Quan aparegui un segon protocol local demostrat, caldrà un descriptor/selector explícit d'identitat, camps, catàleg i còdecs, conservant les façanes actuals. Les propietats cloud d'osmosi/F104 no justifiquen inventar còdecs locals.

Un transport nou implementarà el contracte de trama crua i s'habilitarà només per a maquinari provat. El tipus BroadLink `0x520F` no identifica per si sol el mapa Runxin.

## Regles

- El protocol no importa HA/BroadLink; el transport no interpreta camps.
- Rebre camps, validar significat/unitats i permetre escriptures són decisions diferents.
- `allowed_write_fields` és buit per defecte. El model 1 no té controls, escriptures administratives ni correcció del rellotge; coordinador i adaptador imposen el bloqueig.
- El G6 i Midnight conserven controls i conversions, amb les accions pendents documentades.
- Particularitats futures d'unitats, bytes o enums requereixen fixtures i regressions per als models existents.
- Un ACK no prova l'estat físic; no es reenvien cegament ordres amb resultat ambigu.
- Es conserven codis desconeguts i bytes crus; els camps absents no s'inventen.
- Les lectures provisionals no generen estadístiques de llarg termini.
- Es manté la lectura 1–51 i el camp 52 amb memòria cau independent; no són necessàriament una instantània simultània.
- Es conserven `ypsilon_local`, config-entry v2, identitats MAC, unique IDs i façanes. La migració de la PR #24 és un pilot separat.

El protocol es manté preparat per extreure's a una llibreria quan un altre consumidor real ho justifiqui. La [matriu de suport](model-support.md), la [guia d'Alpha](model-1-alpha.ca.md) i l'[auditoria](multi-model-audit.ca.md) concreten l'estat actual.
