# Auditoria de diversos models — 07/10/2026

[English](multi-model-audit.md) | [Català](multi-model-audit.ca.md)

Revisió del main `7a1dbc6` (2.8.0), el JSON de la issue #17 i la proposta **2.9.0-alpha.1**. La migració de domini de la PR #24 continua com a pilot separat; no s'ha revisat la PR #21. No s'han executat ordres contra dispositius o cloud ni s'ha fusionat/publicat res durant aquesta auditoria.

**L'estructura és una base adequada per als models compatibles que apareixen.** Transport, protocol pur, adaptador, registre de models i HA ja estan separats. No cal duplicar carpetes ni catàlegs per model. Faltava una política efectiva de capacitats: marcar Alpha només era informació i no limitava controls ni rellotge automàtic.

## Millores aplicades

| Problema | Resultat |
|---|---|
| Alta d'un model nou heretava escriptures | Permisos explícits buits per defecte; model 1 només sensors. Bloqueig en serveis, coordinador i adaptador, incloent rellotge i opcions antigues. |
| Conversions encara no demostrades | Resina i quantitat per cicle sense unitat assumida; lectures provisionals i sense estadístiques de llarg termini. |
| Faltaven lectures d'ajustos i bytes per comparar | Sensors de rellotge, horari, duresa, sal i proteccions; parells originals dels camps al diagnòstic. |
| Un permís parcial futur podia mostrar controls aliens | Creació de controls filtrada per camp permès, sense duplicar el còdec. |
| Trama interna massa curta podia provocar error d'índex | Error de protocol explícit abans d'indexar. |
| Resposta de lectura/escriptura podia no correspondre a la petició | Comprovació d'opcode C9/D9 i invalidació si no concorda. |
| Autenticació fallida podia deixar socket obert | Tancament del socket temporal sense alterar l'autenticació ni els errors originals. |
| Text d'error extern podia filtrar dades al JSON normal | Exportació amb missatge fix i metadades estructurades, conservant el text local a HA. |
| Alpha podia publicar-se com a versió estable més recent | Fluxos de release marquen les versions amb guió com a prerelease i no substitueixen latest. |
| Documentació centrada en G6/Midnight | Matriu de suport, arquitectura, guies Alpha en tres idiomes, criteris de nous models i solució d'aparellament com a cas reportat. |

S'han revisat identitat/cicle de vida, catàleg/còdecs/trames, transport/reintents, coordinador/escriptures, entitats/unitats/estadístiques, diagnòstics/cancel·lació/redacció, configuració/serveis, publicació/CI/traduccions i documentació. Les proves conserven el comportament G6/Midnight i cobreixen les noves restriccions.

## Què es conserva

`ypsilon_local`, config-entry v2, identitats MAC i unique IDs, lectura 1–51 i camp 52 amb memòria cau, trames d'escriptura, escala de resina del model 12, calibració/rangs del G6 i controls pendents documentats. Els nous bytes de diagnòstic són metadades; no canvien les lectures. No hi ha dependència cloud, exploració superior al 52 ni escriptures del model 1.

## Què queda pendent

- **Model 1 real:** contrastar resina/quantitat per cicle, altres volums, duresa, cabal, durades i enums; comprovar ús continu i reinicis al seu HA. Rebre camps o zero/false no demostra aplicabilitat.
- **Perfils diferents:** `protocol_profile` descriu el camí F79D actual; encara no és una fàbrica de còdecs. Un segon protocol demostrat requerirà descriptor/selector i fixtures propis. Les dades cloud no identifiquen camps locals.
- **Particularitats:** afegir només overrides d'unitats, bytes, enums o camps demostrats, amb regressions dels models existents. No modificar G6 per adaptar-hi una hipòtesi nova.
- **Migració:** la PR #24 necessita la prova amb còpia de seguretat, validar HACS i integrar els canvis posteriors abans del merge. Aquesta Alpha es pot provar independentment.
- **CI/distribució:** les proves natives són amb HA 2026.9.4/Python 3.14.7/BroadLink 0.19.0. Ni el manifest ni HACS declaren una versió mínima de HA: cal definir-la i provar-la abans de prometre compatibilitat amb versions anteriors. També queda fixar accions flotants a revisions immutables. Una llibreria separada només quan un altre consumidor real ho justifiqui.
- **Instantànies:** el camp 52 pot ser més antic per la memòria cau. Parells rebuts no són paquets capturats ni proves físiques de conversions.

L'[informe detallat](multi-model-audit.md) enumera abast i límits. Les comprovacions de programari i CI es registren a la PR; no substitueixen les validacions del propietari del dispositiu.

Resultats locals: **253 proves superades** amb HA 2026.9.4/Python 3.14.7; **118 superades i 3 mòduls de HA omesos** en un entorn independent amb Python 3.13.15. Les auditories de publicació, arquitectura/traduccions/protocol i cobertura de camps han passat. HA emet un avís de deprecació d'`aiohttp`. També s'ha comprovat la sincronització inicial del rellotge del G6/Midnight i el bloqueig si la lectura fresca identifica un model de només lectura.

Seguiment: el [segon informe](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6045265175), generat des de HA 2026.9.4 amb la integració 2.8.0, torna a rebre els 52 camps en dues consultes sense errors ni reintents. Model 1, firmware 62016 i valors de resina/cicle pendents de contrast es mantenen. El restant de referència baixa de 1304 a 1284 i el consum diari puja de 215 a 235: tots dos varien en 20. És una coherència útil entre instantànies, però no valida unitats ni aplicabilitat amb l'app. Una segona fixture conserva només els parells dels camps i cobreix aquesta evidència.
