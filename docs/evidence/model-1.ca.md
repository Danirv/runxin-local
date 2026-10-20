# Model 1 / F150: registre d’evidència

Observacions datades, valors reportats i límits. La [guia actual](../models/model-1.ca.md) descriu alta i controls. Aquest registre no és una petició de proves noves.

[English](model-1.md) | [Català](model-1.ca.md) | [Español](model-1.es.md) · [Documentació](../index.md)

## Punts de calibració per camp

| Camp | Referència del JSON | Què falta confirmar |
|---|---|---|
| 26, resina | `F0 00`, primer byte 240 | Valor, nom i unitat de l'app. HA mostra 240 sense litres ni multiplicador assumit. |
| 41–42, quantitat per cicle | 15 | L’usuari va canviar 24 → 15 a Runxin Advanced → Water treatment capacity. Cal confirmar la unitat i la correspondència amb aquest camp; HA manté 15 sense unitat assumida. |
| 35–36, restant | 1304 L | Capacitat restant amb la seva unitat, prop de l'hora de lectura. |
| 37–40, consum diari/mitjana | 215 / 192 L | Consum del dia i mitjana del controlador; no confondre-la amb un total de l'historial setmanal. |
| 47, duresa | 280 mg/L | Nom exacte i escala de duresa. |
| 43, sal afegida | 25 kg | Registre de sal afegida, no nivell físic del dipòsit. |
| 4/5/10, hores | 20:38 / 00:00 / 00:00 | Rellotge i horari de regeneració visibles. |
| 6/7/15/17/19/21/23 | Proteccions i durades | Comparar els ajustos que l'app mostri, sense modificar-los. |

El consum diari s’ha contrastat amb el controlador físic; la resta conserva la interpretació F79D compartida segons l’evidència disponible. La resina i la quantitat per cicle no tenen unitat confirmada. Es conserva el segon byte de resina sense deduir un còdec U16. El camp 52 es llegeix amb memòria cau independent i pot ser anterior a la resta de la instantània.

La [issue #17](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6044822202) confirma BL3372 `0x520F`, firmware 62016, autenticació amb l'app tancada, model 1 estable i resposta dels 52 camps en dues consultes sense errors. La fixture conserva només els parells publicats: les trames reconstruïdes són sintètiques. Les proves de programari no validen conversions físiques.

Una calibració futura es farà al model 1, sense canviar les conversions del G6/Midnight. Aquest suport no explora camps superiors al 52; el rellotge manual (camp 4) està verificat a l’equip reportat; la resta d’escriptures opcionals continuen pendents.


## Confirmacions incorporades a la 2.9.3

La [resposta del 10-10-2026](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6096161743) confirma rellotge inicial 11:23, escriptures a 11:24 i 11:26 i restauració amb el botó de sincronització manual. La pantalla del controlador i Water Device coincideixen després de cada acció. Només es va provar el camp 4 i després es va desactivar l’opció experimental. No valida la correcció automàtica ni altres escriptures.

La pantalla física és en neerlandès amb codi d’idioma 7. HA corregeix només aquesta correspondència del model 1, sense escriure l’idioma ni canviar la llengua de l’app.

L’equip té 24 L nominals de resina, però el camp 26 continua `F0 00` (referència 240) i els camps 41–42 continuen en 15. Al frontend del fabricant, `resinVolume` és Resin volume i `periodicWaterProduction` és Water treatment capacity. No hem confirmat independentment quin camp local modificava aquella pantalla de l’app Runxin antiga. `240 / 10 = 24 L` és plausible, però encara no és un contrast amb el valor configurat. Es mantenen les dues lectures sense unitat assumida i no s’aplica el còdec U16 del model 14.

El volum de resina ha de descriure la càrrega real, no ajustar-se al nombre de persones. La capacitat de tractament és un altre paràmetre que depèn de resina, duresa i ajustos de regeneració; reduir-la mantenint els cicles pot fer regenerar més sovint en lloc d’estalviar. Cal aclarir l’etiqueta/unitat i seguir les instruccions de l’equip abans de proposar un canvi. No cal tornar a aparellar, recuperar l’app antiga, repetir diagnòstics ni modificar ajustos per aclarir les lectures.


## Funcionament reportat després de regenerar amb la 2.9.3

La [resposta posterior del 10-10-2026](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6101162421) confirma lectures periòdiques normals i recuperació dels valors després dels reinicis de HA en actualitzar. L’equip reporta model 1, firmware BL3372 62016 i integració 2.9.3.

A les 19:41:45, hora local, HA mostrava aspiració de salmorra i esbandida lenta mentre el controlador indicava **“pekel-spoel traag up-flow”**. Això contrasta aquella fase concreta. HA havia indicat ompliment de salmorra a les 19:35:34, uns sis minuts abans. Amb lectures cada 60 segons, aquesta observació no valida independentment la durada configurada ni demostra un error respecte dels set minuts de la lectura anterior. Els intents avortats anteriors s’exclouen de la validació de seqüència i durades. L’opció de regeneració de HA estava desactivada: no valida l’ordre d’inici del camp 34.

Després del cicle, HA mostrava capacitat restant **3429 L**, davant dels **1267 L** reportats el 8 d’octubre. Es registra una recuperació de capacitat després de regenerar, sense calibració independent de la unitat. Es mantenen duresa 280 mg/L, resina `F0 00` / referència 240 i referència per cicle 15. Si la duresa és expressada com CaCO₃, `3,429 m³ × 28 °f ≈ 96 °f·m³`, uns `4 °f·m³/L` per als 24 L nominals de resina. És una comprovació de coherència, no un contrast amb la resina configurada ni una prova de l’escala 0,1. L’usuari recorda una etiqueta L al costat de l’ajust antic, però no n’està segur; la unitat i la correspondència exacta amb el camp local continuen pendents.

Aquest informe incorpora evidència de funcionament i d’una fase. La 2.10.2 promou les lectures a Beta, sense canviar còdecs, permisos ni les dues unitats pendents. Les comparacions anteriors són punts de calibració pendents: no es demanen més proves, captures ni diagnòstics a aquest contribuent. La incidència original de connexió/alta es pot tancar independentment d’aquestes validacions.
