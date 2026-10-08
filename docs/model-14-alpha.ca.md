# Model 14 / Runxin F136: suport Midnight Alpha

[English](model-14-alpha.md) | [Català](model-14-alpha.ca.md) | [Español](model-14-alpha.es.md)

Runxin Local **2.9.0** admet el model **14 / F136** amb BL3372 (`0x520F`) i el protocol compatible F79D existent. La release és estable; **Alpha** descriu el suport d’aquest controlador, inicialment el Euro-Clear Midnight 25 / ECOPRO+ de la [issue #22](https://github.com/Danirv/runxin-local/issues/22).

L’usuari va afegir el model localment i declara que funcionen descoberta, autenticació, lectures i el mapa del model 12. Acceptem com a evidència aportada les escriptures que declara verificades: **4 (rellotge), 6 (límit de temps de cabal), 10 (hora de regeneració) i 43 (sal afegida)**. **7 (llindar de cabal), 34 (accions mecàniques) i 47 (duresa)** continuen pendents.

Instal·la 2.9.0 o posterior, reinicia HA i afegeix Runxin Local. No cal editar el registre. Una entrada operativa que ja funcionava amb la modificació local es pot actualitzar conservant domini i identificadors MAC; revisa qualsevol altra modificació local abans de substituir la carpeta. Una entrada de només diagnòstic no es transforma: descarrega l’informe i elimina-la abans d’afegir el dispositiu operatiu.

S’ofereixen els sensors i controls Midnight, inclosa la correcció automàtica del rellotge, els ajustos, el botó de regeneració i els serveis validats. Es mantenen codificacions, rangs, comprovacions d’estat i lectura posterior estricta. Els controls pendents continuen disponibles per validar-los; vacances segueix de només lectura.

La resina utilitza **primer byte cru × 0,1 L**, com el model 12, a partir del mapa compartit declarat. Falta la comparació directa entre bytes del model 14 i pantalla/app: el sensor i els diagnòstics mostren `resin_volume_scale_confirmed=false` i conserven els dos bytes. Els enums no reconeguts continuen visibles.

Són útils els diagnòstics guardats de HA, l’entrada exacta que va afegir i els valors/unitats de resina i altres lectures de l’app o pantalla. No cal repetir proves completades; es poden aportar els resultats inicials/canvi/lectura/restauració ja disponibles. No cal iniciar una acció mecànica només per fer l’informe. [Verificació física](hardware-verification.ca.md).
