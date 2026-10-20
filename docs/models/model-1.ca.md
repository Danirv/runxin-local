# Model 1 / F150

[English](model-1.md) | [Català](model-1.ca.md) | [Español](model-1.es.md) · [Matriu de suport](../model-support.md) · [Documentació](../index.md)

**Lectures Beta i rellotge manual validat.** F150 és el nom de l’API del fabricant per al codi 1, no una identitat comercial confirmada. L’evidència prové de l’equip sense marca de la issue #17, BL3372 `0x520F`, firmware 62016; no valida totes les vàlvules etiquetades F150.

## Instal·lació

Segueix la [instal·lació i actualització](../installation.ca.md). Conserva les entrades operatives; elimina una entrada només de diagnòstic abans de donar d’alta el mateix dispositiu. L’alta explica les unitats pendents. Per defecte consulta cada 60 segons amb sondeig adaptatiu desactivat.

## Què permet

- Lectures normals d’estat, aigua i diagnòstic, amb consum diari `total_increasing` per a Energia. La mitjana setmanal no és un comptador acumulatiu.
- **Rellotge i sincronització manuals (camp 4)**, contrastats amb app/controlador, sense opció experimental.
- Sensors de referència, bytes rebuts i metadades de permisos. Alguns diagnòstics estan deshabilitats per defecte.
- **Resina i capacitat per cicle sense unitat ni estadístiques.** `F0 00` / referència 240 no determina litres ni multiplicador; la referència 15 per cicle és un altre paràmetre. Aquestes dues incerteses no bloquegen les altres estadístiques.

Rellotge automàtic, escriptures del llindar de cabal (7), vacances i avanç directe de fases continuen bloquejats. El codi d’idioma 7 està confirmat com a neerlandès en aquest model; altres enums mantenen interpretacions de referència.

## Ajustos experimentals opcionals

A **Configuració → Dispositius i serveis → Runxin Local → Configura**, l’opció d’ajustos experimentals, desactivada per defecte, habilita els camps **6/10/43/47**: temps de cabal continu, hora de regeneració, sal afegida i duresa. Les escriptures continuen pendents de verificació física al model 1.

Una segona opció desactivada per defecte permet només **iniciar regeneració (34)** i també requereix els ajustos experimentals. No permet avançar fases arbitràriament. Una validació física futura pot aprofitar un cicle normalment previst; no és necessària per obtenir un informe.

En una prova voluntària reversible, parteix d’una lectura nova, modifica un únic valor permès, compara lectura HA i app/controlador, restaura i comprova la restauració. Una resposta perduda no justifica repetir l’ordre a cegues. Desactivar les proves revoca/substitueix la sessió i elimina controls addicionals, conservant rellotge manual, lectures, identificadors i memòria cau.

## Evidència i punts pendents

El [registre datat](../evidence/model-1.ca.md) conserva valors crus, restauració del rellotge, idioma, fases i distinció entre resina i capacitat de tractament. La [verificació física](../hardware-verification.ca.md) inclou els contrastos posteriors del consum diari.

No es demanen més proves ni informes al col·laborador de la issue #17. La calibració pendent és independent de resoldre aquella incidència. Descarregar diagnòstics d’una entrada normal exporta l’estat en memòria cau, sense una exploració nova.
