# Seguiment d'arquitectura i documentació — 08/10/2026

[English](audit-followup.md) | [Català](audit-followup.ca.md) | [Español](audit-followup.es.md)

Continua l'auditoria del conjunt després de la PR #25 i **2.9.0-alpha.1**, des de main `036b808`. L'[auditoria inicial](multi-model-audit.ca.md) recull la implementació Alpha; aquest document segueix els pendents comuns. La PR #21 queda exclosa i la migració continua separada a la PR #24.

L'estructura transport / protocol pur / adaptador / política de model / HA és adequada per als models observats. Comparteixen el còdec quan les dades ho demostren i només incorporen diferències d'unitats, permisos o aplicabilitat contrastades. No cal duplicar carpetes per model. Una família realment diferent necessitarà descriptor, catàleg, fixtures i selecció propis; `protocol_profile` encara és metadada descriptiva.

## Millores aplicades

- Auditoria d'imports recursiva: detecta sortides del paquet pur per imports relatius, dependències de xarxa i acoblament al transport. Els transports no poden importar catàlegs/semàntica ni l'adaptador HA; errors i trames neutrals són admissibles.
- Diagnòstics amb `write_policy`: identitat configurada/observada, bloqueig del coordinador/adaptador, intersecció de camps permesos i rellotge sol·licitat/permès. L'evidència del model continua separada. L'exportació només consulta memòria cau.
- Suite completa amb HA 2026.9.3 i 2026.9.4, Python 3.14, i versions fixades de les eines. No es declara una versió mínima de HA.
- Fonts de les accions checkout/setup-python/HACS/hassfest fixades a commits; l'auditoria rebutja referències flotants. Dependabot conserva les actualitzacions setmanals.
- Guies de contribució/publicació en EN/CA/ES alineades amb les proves completes, prereleases, marca Runxin Local i política compartida.

**Límit de CI:** els descriptors HACS/hassfest encara executen contenidors amb tags flotants; fixar-ne la font no fixa els contenidors ni totes les dependències transitives. L'auditoria d'imports és estàtica, no un sandbox.

Es conserven còdecs, conversions/rangs G6/model 12, trames, lectures, domini, config-entry v2 i unique IDs. No s'habiliten ordres noves. Els canvis runtime només afegeixen metadades de diagnòstic.

## Pendents concrets

| Punt | Què falta | Pas següent |
|---|---|---|
| Model 1 | Unitats/etiquetes de l'app i lectures properes, primer resina 240 i quantitat per cicle 15 | Comparacions de la issue #17 i correcció/fixture específica, sense multiplicadors suposats ni controls. |
| Model 12 | Validació dels camps 7/47/34 i funcionament sostingut | Proves del propietari segons la guia de maquinari; Alpha actual intacta. |
| G6 mecànica/vacances | Comportament físic del camp 34 i acció local de vacances demostrada | Treball de maquinari separat; el camp 49 continua exclòs. |
| Model 14/altres | Informes coherents i comparacions; IDs/còdecs locals reals per als camps addicionals | Només diagnòstic. Les propietats cloud no identifiquen camps locals superiors al 52. |
| Migració de domini | Pilot HA amb còpia, registres/automatitzacions, camí HACS i actualització amb main | Continuar la PR #24 separadament quan el mantenidor pugui provar-la. |
| HA anteriors | Un objectiu anterior concret i proves natives | Només s'han provat 2026.9.3/2026.9.4; no afirmar suport anterior ni fixar un mínim sense dades. |
| Contenidors de validació | Digests compatibles verificats i procés d'actualització | Revisió posterior; continuar la validació upstream. |
| Llibreria separada | Un segon consumidor real i contracte de distribució/versionat | Conservar el paquet pur al repositori fins que es justifiqui. |

El camp 52 continua en memòria cau separada i pot ser anterior a la resta. Rebre zero/false no demostra aplicabilitat física.

## Validació i publicació

Usa entorns separats amb `requirements-test-offline.txt`, `requirements-test-ha.txt` i `requirements-test-ha-baseline.txt` i executa `python -m pytest -q` a cadascun. Consulta [CONTRIBUTING](../CONTRIBUTING.ca.md) per a publicació, auditoria, cobertura de camps i compilació. Les proves simulen l'E/S i no substitueixen maquinari.

Aquest manteniment és **Unreleased**: no mou ni substitueix el tag Alpha publicat. Cal una versió nova conjunta de manifest/changelog/info abans de distribuir-lo. El mantenidor decideix la fusió/publicació.

Resultats locals: **275 proves superades amb cada versió de HA**, **136 superades / 3 mòduls HA omesos** offline, i comprovacions de publicació, arquitectura, camps, YAML/shell, enllaços relatius, diff i compilació. HA emet un avís upstream de deprecació d’aiohttp. Els checks finals de GitHub consten a la PR.
