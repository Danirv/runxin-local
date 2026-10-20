# Model 12 / F105: Euro-Clear Midnight

[English](model-12.md) | [Català](model-12.ca.md) | [Español](model-12.es.md) · [Matriu de suport](../model-support.md) · [Documentació](../index.md)

**Beta**, limitat al Euro-Clear Midnight 25 provat amb capçal ECOPRO+ i BL3372 `0x520F`, que retorna codi de controlador 12. F105 és el nom de l’enum de l’API; no equival a qualsevol referència comercial de vàlvula.

## Alta i controls

Segueix la [instal·lació i actualització](../installation.ca.md) i conserva les entrades operatives. Hi ha lectures/estadístiques normals, rellotge, hora de regeneració, duresa, sal afegida, protecció de cabal continu i els controls de regeneració/serveis existents. El rellotge automàtic segueix les opcions normals. Vacances és només lectura.

| Evidència d’escriptura | Camps |
|---|---|
| Verificats físicament a l’equip reportat | 4 rellotge, 6 temps de cabal continu, 10 hora de regeneració, 43 sal afegida |
| Pendents de verificació, amb permisos existents conservats | 7 llindar de cabal, 47 duresa, 34 regeneració/accions mecàniques |

Lectures coincidents no validen escriptures. Es mantenen rangs, unitats, política per model i reconciliació amb lectura nova. Beta no modifica permisos ni representa proves físiques noves.

## Resina, enums i duresa

El camp 26 `FA 00` conserva **U8 × 0,1** i mostra **25 L** al Midnight 25 provat. Es guarden tots dos bytes; aquesta captura no determina el significat del segon. No s’ha de copiar el còdec U16 del model 14. La resina és un paràmetre configurat, no una mesura del contingut físic.

El patró de treball **255** i mode de relé **2** es mostren com a decimals amb `raw_code`; els manuals consultats no en demostren les etiquetes de protocol. Les dades absents continuen desconegudes.

El manual Midnight utilitza una convenció de duresa pròpia (graus alemanys × 10, amb una referència CaO mg/L en una altra pàgina). Conserva el valor reportat i compara les unitats exactes del controlador/manual; no substitueixis silenciosament l’escala ni la generalitzis al G6.

## Evidència

El [registre físic](../hardware-verification.ca.md#euro-clear-midnight--model-de-controlador-12) recull lectures, canvis/restauracions, sincronització del rellotge, manuals i punts pendents. Si l’app no funciona amb l’equip, la pantalla del controlador pot aportar el contrast independent. Les escriptures opcionals futures es documenten separadament de les lectures.
