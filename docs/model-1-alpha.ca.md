# Controlador model 1 / F150: Alpha, només lectura per defecte

[English](model-1-alpha.md) | [Català](model-1-alpha.ca.md) | [Español](model-1-alpha.es.md)

La versió **2.9.0** admet el codi de controlador **1** amb sensors de lectura periòdica. El fabricant anomena aquest codi **F150**, però no tenim confirmat el producte comercial ni la vàlvula de la issue #17. No és suport general per a qualsevol equip F150.

La release de la integració és estable; Alpha descriu només el suport d’aquest model.

## Instal·lació i comparació

1. Instal·la la versió 2.9.0 o posterior amb HACS, o descarrega el ZIP de la release i copia només `custom_components/ypsilon_local` a `/config/custom_components/ypsilon_local`. Desa una còpia de la carpeta anterior i reinicia HA. Aquesta Alpha conserva `ypsilon_local`; no necessita la migració a `runxin_local`.
2. Si tens una entrada de només diagnòstic del mateix dispositiu, descarrega primer el seu informe i elimina aquesta entrada abans de donar d'alta el dispositiu normalment. No es transforma automàticament en una entrada amb sensors.
3. Afegeix **Runxin Local**, indica la IP local i accepta l'explicació **Alpha de només lectura**. Per defecte llegeix cada minut, sense cadència adaptativa. La correcció del rellotge està bloquejada encara que hi hagi una opció antiga activada.
4. Compara els sensors amb l'app que funciona. Algunes entitats de diagnòstic estan desactivades per defecte; activa les que necessitis des de la llista d'entitats. No cal canviar ajustos per comparar-los.
5. Des del menú de l'entrada de la integració, **Descarrega els diagnòstics** i adjunta el JSON a la issue existent, juntament amb uns valors o captures de l'app, les unitats i l'hora aproximada. Exportar el diagnòstic no inicia una altra exploració. Oculta dades identificatives a les captures.

L'entrada normal autentica i fa lectures LAN periòdiques; no és una captura passiva. Si l'app i HA interfereixen, pausa les lectures o desactiva temporalment l'entrada mentre fas les captures, sense tornar a aparellar l'equip. Es conserven el domini, la versió de config entry i les identitats existents del G6 i Midnight.

## Què permet

- Sensors d'estat, aigua, durades i diagnòstic amb interpretació **F79D de referència**.
- Sensors equivalents per al rellotge, horari de regeneració, duresa, sal afegida, temps de cabal continu, tall per cabal brut i codi de motiu de tancament.
- Dos bytes originals per camp rebut a `state._rawFieldBytes`, i atributs de referència a les entitats. No s'exporten paquets complets, claus ni sessions.
- Metadades de model, evidència i permisos. Rebre zero o false no demostra que una funció sigui aplicable.

**Per defecte no hi ha controls number, time ni button**, ni correcció del rellotge ni ordres de configuració o mecàniques. Els serveis administratius també rebutgen escriptures. El coordinador i l'adaptador del client imposen la política independentment de la interfície; a la 2.9.1 es poden activar les proves manuals opcionals descrites a continuació.

Les lectures són provisionals i no generen **estadístiques de llarg termini**. HA encara pot desar l'historial ordinari. Les etiquetes enum són de referència i els codis desconeguts es mantenen visibles.

## Comparacions prioritàries

| Camp | Referència del JSON | Què falta confirmar |
|---|---|---|
| 26, resina | `F0 00`, primer byte 240 | Valor, nom i unitat de l'app. HA mostra 240 sense litres ni multiplicador assumit. |
| 41–42, quantitat per cicle | 15 | Nom i unitat reals. HA mostra 15 sense litres; potser no representa capacitat d'aigua tractada. |
| 35–36, restant | 1304 L | Capacitat restant amb la seva unitat, prop de l'hora de lectura. |
| 37–40, consum diari/mitjana | 215 / 192 L | Consum del dia i mitjana del controlador; no confondre-la amb un total de l'historial setmanal. |
| 47, duresa | 280 mg/L | Nom exacte i escala de duresa. |
| 43, sal afegida | 25 kg | Registre de sal afegida, no nivell físic del dipòsit. |
| 4/5/10, hores | 20:38 / 00:00 / 00:00 | Rellotge i horari de regeneració visibles. |
| 6/7/15/17/19/21/23 | Proteccions i durades | Comparar els ajustos que l'app mostri, sense modificar-los. |

Totes les unitats són interpretacions de referència pendents de contrast. La resina i la quantitat per cicle no tenen unitat confirmada. Es conserva el segon byte de resina sense deduir un còdec U16. El camp 52 es llegeix amb memòria cau independent i pot ser anterior a la resta de la instantània.

La [issue #17](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6044822202) confirma BL3372 `0x520F`, firmware 62016, autenticació amb l'app tancada, model 1 estable i resposta dels 52 camps en dues consultes sense errors. La fixture conserva només els parells publicats: les trames reconstruïdes són sintètiques. Les proves de programari no validen conversions físiques.

Una calibració futura es farà al model 1, sense canviar les conversions del G6/Midnight. Aquesta Alpha no explora camps superiors al 52; les escriptures manuals opcionals encara no estan verificades físicament.

## Proves manuals opcionals (2.9.1)

A l’entrada operativa del model 1, obre **Configuració → Dispositius i serveis → Runxin Local → Configura**. Activa **els ajustos experimentals del model 1** i desa. La recàrrega afegeix controls manuals per a rellotge (4), límit de temps de cabal (6), hora de regeneració (10), sal afegida (43) i duresa (47). **Totes les escriptures continuen pendents de verificació física**.

Anota una lectura inicial nova, canvia un sol ajust una quantitat petita dins del rang, comprova la lectura posterior i la pantalla/app si és visible, restaura el valor original i confirma’l. Aporta camp, valor inicial, sol·licitat, llegit, unitat/pantalla i restauració. No repeteixis una ordre amb resultat ambigu: la integració comprova l’estat sense reenviar-la a cegues.

Una **segona opció** permet iniciar una regeneració prevista i requereix també el mode d’ajustos. El botó comprova servei i vacances desactivades amb una lectura nova, envia camp 34 = 1 una sola vegada i comprova la fase. L’avanç directe de fases continua bloquejat, també als serveis administratius.

El **rellotge automàtic**, el **camp 7**, vacances i escriptures de resina/capacitat continuen bloquejats. El dispositiu va retornar unitat 1; el control de llindar de cabal està calibrat per a unitat 2. Les lectures de resina i capacitat encara són provisionals.

Desactivar els ajustos torna a només lectura i desactiva també la prova de regeneració. Es revoca i substitueix la sessió anterior; es conserven sensors, identificadors, bytes crus i absència d’estadístiques provisionals. Els diagnòstics separen evidència del model i `write_policy` efectiu. Exportar-los no inicia lectures ni escriptures. El G6 i els models 12/14 mantenen la seva política.
