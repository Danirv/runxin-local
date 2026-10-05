# Ypsilon per a Home Assistant

Integració local per a descalcificadors compatibles amb **Runxin F79D + BroadLink BL3372**, amb el Ypsilon G6 com a maquinari de referència i suport experimental per al Euro-Clear Midnight.

- Descobriment DHCP i configuració manual per IP.
- Lectura local de cabal, consum diari, capacitat restant, fase de vàlvula, mode de regeneració, patró de treball i avisos.
- Escriptures amb lectura física posterior estricta: un ACK no es considera estat confirmat.
- Controls de duresa, quantitat de sal afegida, proteccions de cabal/temps, hora de regeneració, rellotge i regeneració forçada; l'evidència física es documenta per camp i model.
- Estat de vacances de només lectura; la 2.6.1 retira el switch de vacances perquè l'escriptura local directa del camp 49 no va quedar confirmada físicament al G6 provat.
- Diagnòstics per fases de rentat, dissolució de sal, pausa 1, errors, comunicació i manteniment.
- Traduccions CA/ES/EN i branding local amb icona quadrada i logo horitzontal independents.

## Compatibilitat nova a la 2.7.0

El **Euro-Clear Midnight (controlador model 12)** té suport **experimental / Alpha**, provat amb un Midnight 25 amb capçal ECOPRO+ i BroadLink BL3372 (`0x520F`). Les captures concorden amb la pantalla del controlador; les escriptures dels camps 4, 6, 10 i 43 estan verificades físicament. Els camps 7 i 47 i les accions mecàniques del camp 34 continuen disponibles per fer proves, però encara no estan verificats en aquest model.

Alpha afecta només la compatibilitat del model 12. Es conserven els controls i la verificació estricta del PR original; el suport del G6 no canvia. Els diagnòstics inclouen l'evidència per model i els dos bytes crus del camp 26. `FA 00` es continua mostrant com **25 L**; aquesta captura no determina el significat del segon byte ni el còdec de volums superiors a 25,5 L.

Consulta les [proves pendents del model 12](hardware-verification.ca.md#euro-clear-midnight--model-de-controlador-12).

## Canvi principal de la 2.6.3

El camp 7 (`flowRateOff`, llindar de tancament per cabal) torna a utilitzar **u16 big-endian** en lectura i escriptura i recupera `HARDWARE_WRITE_VERIFIED`.

La prova física és directa: el controlador retorna `03 E8` mentre l'app oficial mostra 10,00 m³/h. En BE és raw 1000; en LE es converteix erròniament en 59395 i Home Assistant mostrava 593,95 m³/h. Per escriure 2,00 m³/h, raw 200 s'ha d'enviar com `00 C8`. La regressió LE enviava `C8 00`, rebia ACK però el read-back físic no confirmava el canvi, i la verificació estricta de Ypsilon el rebutjava correctament.

Versions anteriors del projecte amb BE ja havien verificat físicament SET/read-back per aquest camp. La superfície HA es manté limitada a 0–10,00 m³/h en la família d'unitat 2 validada.

## Canvis principals de la 2.6.1

- Vacances: el camp 49 es continua llegint i el sensor `desactivat / preparant / actiu` es manté, però no s'exposa cap escriptura fins conèixer i verificar físicament l'acció local del firmware actual.
- Consum diari: es manté com a comptador `TOTAL_INCREASING` que creix durant el dia i es reinicia al canvi de dia.
- Camp 39: **Consum setmanal mitjà del controlador**. No és el total setmanal de les barres històriques de l'app oficial.
- Camp 41: **Capacitat de tractament per cicle**, no un comptador de consum.
- Camp 43: **Quantitat de sal afegida**, un valor de registre/configuració en kg; no és nivell de sal restant.
- Branding amb icona quadrada, logo horitzontal i variants 2x/dark.

## Estadístiques antigues de Home Assistant

Versions anteriors van crear estadístiques de llarg termini per al consum mitjà setmanal i la capacitat per cicle quan encara declaraven `state_class`. Després d'actualitzar, Home Assistant pot oferir eliminar aquelles estadístiques obsoletes. És correcte eliminar-les: això no elimina l'entitat ni l'històric normal del Recorder.

## Instal·lació

Amb HACS, afegeix `https://github.com/Danirv/ypsilon-local` com a repositori personalitzat de tipus **Integration** fins que quedi incorporat al catàleg per defecte. Manualment, copia `custom_components/ypsilon_local` a `/config/custom_components/ypsilon_local`.

## Consum d'aigua

Per a consum acumulat utilitza **Consum diari**. **Cabal** és una mostra instantània i pot no veure consums molt curts entre dos polls. Per obtenir un total real de la setmana a Home Assistant, deriva'l del comptador diari/estadístiques; no utilitzis el camp 39 com si fos el total de la setmana actual.

## Problemes de connexió

Consulta la [guia de resolució de problemes](troubleshooting.ca.md) per distingir descoberta, autenticació rebutjada i lectures F79D. Inclou logs de depuració i un script que genera un informe sense identificadors ni claus, encara que no puguis completar la configuració a HA.

## Seguretat

La integració pot canviar paràmetres i iniciar moviments de vàlvula. No és un controlador de seguretat certificat ni ha de ser l'única protecció contra fuites o inundacions. Conèixer el còdec no equival a verificar l'acció física. En la compatibilitat Alpha del model 12, els controls pendents es mantenen disponibles amb aquesta limitació documentada.

Consulta el [README principal](../README.md), [`waterdevice-audit.ca.md`](waterdevice-audit.ca.md), [`f79d.ca.md`](f79d.ca.md), [`hardware-verification.ca.md`](hardware-verification.ca.md), [SECURITY](../SECURITY.md) i [LEGAL](../LEGAL.md).
