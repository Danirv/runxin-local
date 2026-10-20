# Utilitzar Runxin Local

[English](usage.md) | [Català](usage.ca.md) | [Español](usage.es.md) · [Documentació](index.md)

## Entitats i controls

Les entitats operatives mostren cabal, consum diari, capacitat restant, estat, mode de regeneració, patró de treball, vacances i avisos actius. A Diagnòstic hi ha durades/comptadors de fases, recordatoris, resina, identitat i comunicació. Algunes entitats estan deshabilitades per defecte; activa-les a la llista d’entitats del dispositiu si les necessites.

Els controls depenen del [model](model-support.md). Els models 9/12/14 conserven rellotge, hora de regeneració, duresa, sal afegida, proteccions, botó de regeneració i serveis administratius; les validacions pendents es documenten separadament dels permisos. El model 1 només ofereix rellotge manual validat per defecte, amb opcions explícites per a altres proves. [Guia](models/model-1.ca.md).

Una dada absent no es converteix en zero. Els enums desconeguts mostren el codi decimal i `raw_code`; les etiquetes conegudes segueixen el mapa de referència i les excepcions confirmades per model.

## Consum d’aigua i estadístiques

| Entitat | Significat | Estadístiques HA |
|---|---|---|
| Consum diari | Comptador acumulat del dia; es reinicia al canvi de dia | `total_increasing`; font d’aigua del panell d’Energia |
| Cabal | Última mostra instantània | `measurement`; pot no mostrar consums curts entre consultes |
| Capacitat de tractament restant | Quantitat restant del controlador, no aigua emmagatzemada | `measurement` |
| Consum setmanal mitjà del controlador | Mitjana informada pel controlador, no el total històric de l’app | Sense classe estadística |
| Capacitat de tractament per cicle | Quantitat del cicle de tractament, no aigua consumida | Sense classe estadística |

Després de l’alta o d’actualitzar el model 1, espera que HA reculli estadístiques i selecciona **Consum diari** com a font d’aigua a Energia. Conserva les entitats existents. No es recuperen retroactivament estadístiques de llarg termini que no es van generar.

Per obtenir el consum de la setmana, deriva’l del comptador diari/historial. Si HA ofereix eliminar estadístiques antigues de la mitjana setmanal o capacitat per cicle, aquella neteja no elimina les entitats ni l’històric normal del Recorder.

Les unitats segueixen el selector del controlador. Resina i capacitat per cicle del model 1 continuen **sense unitat**, multiplicador assumit ni estadístiques. Els models 12 i 14 utilitzen còdecs de bytes diferents per a la resina; consulta la [política](model-support.md).

## Sal, resina i manteniment

**Quantitat de sal afegida** és l’ajust 43 del controlador (0–100 kg), no un nivell físic del dipòsit. La integració escriu el valor demanat: enviar dues vegades 25 kg no implementa un acumulador de 50 kg a HA. No estima ni resta sal després de regenerar. Concentració baixa de salmorra i recordatori de sal són senyals separats.

El volum de resina és un paràmetre configurat, no una mesura del contingut físic. La capacitat nominal pot diferir del valor configurat. El llindar de regeneracions per al recordatori de resina no és el recompte de cicles fets.

## Opcions de consulta i rellotge

A **Configura**, l’interval normal és de **60 segons** i l’adaptatiu de **10 segons** amb cabal o transició mecànica observada. Als models 9/12/14, el sondeig adaptatiu i la correcció automàtica del rellotge estan activats per defecte. La tolerància del rellotge és de **2 minuts**; el canvi estacional pot provocar-ne una correcció.

El model 1 comença amb 60 segons fixos i sondeig adaptatiu desactivat. El rellotge automàtic queda bloquejat independentment de l’opció desada; el rellotge i la sincronització manuals continuen disponibles. Els ajustos experimentals i l’inici de regeneració són opcions separades desactivades per defecte.

El camp 52 es refresca independentment cada **3600 segons** i es desa en memòria cau. Els bytes dels diagnòstics poden tenir antiguitats diferents; no tots els camps s’han consultat necessàriament junts.

## Vacances i regeneració

Vacances és només lectura: `off` si el flag és fals; `preparing` si és cert abans d’arribar a l’estació estable 8; `active` si és cert i l’estació és 8. L’estat operatiu cru es conserva. Vacances estable no manté la consulta ràpida.

El botó de regeneració exigeix una lectura nova en servei amb vacances desactivades, rebutja peticions simultànies, envia una ordre i comprova la fase resultant. Mou la vàlvula i utilitza aigua/sal. Un ACK no prova un canvi; els resultats ambigus es contrasten amb lectures noves sense repetir l’ordre a cegues. La [verificació física](hardware-verification.ca.md) concreta què s’ha provat per model.

## Serveis avançats

**`ypsilon_local.write_fields`** és administratiu i admet ajustos reversibles permesos, amb validació de valor cru, rang i unitat. **`ypsilon_local.advance_phase`** gestiona separadament l’avanç de fases. Tots dos apliquen els permisos efectius; les entrades de diagnòstic no poden escriure. El model 1 no permet avançar fases i el camp 49 no té escriptor HA.

Per a l’ús habitual, utilitza els controls d’entitat. La capacitat del còdec és més àmplia que els permisos HA; consulta el [catàleg](f79d.ca.md) per interpretar valors crus.

## Diagnòstics i ajuda

**Descarrega diagnòstics** d’una entrada operativa exporta dades en memòria cau sense iniciar una altra consulta. L’[informe de compatibilitat](compatibility-report.md) fa lectures puntuals explícites i acotades; l’entrada desada no té entitats, consultes periòdiques ni controls. Per a errors de connexió, consulta la [guia](troubleshooting.ca.md).
