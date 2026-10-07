# Prova de migració a runxin_local

La branca `feat/runxin-domain-migration` és **experimental (3.0.0-alpha.1)**.
La versió estable 2.8.x continua amb `ypsilon_local`. Aquesta prova no és una
actualització normal de HACS: abans de posar el nou codi en marxa cal migrar la
configuració amb **Home Assistant Core aturat**.

L'eina no contacta amb el descalcificador. Conserva els IDs de configuració,
dispositius i entitats, els noms personalitzats, les àrees, les opcions i els
informes de diagnòstic. No modifica la base de dades d'històric, les estadístiques,
les automatitzacions ni els dashboards. Els dos serveis antics continuen com a
àlies dels nous, amb les mateixes comprovacions.

Això no garanteix que totes les referències arbitràries continuïn funcionant:
cal revisar plantilles que filtrin pel domini, el logger
`custom_components.ypsilon_local` i eventuals automatitzacions de dispositiu
que incloguin explícitament el domini anterior.

## 1. Preparar-ho sense modificar res

- Fes i descarrega una **còpia completa de Home Assistant**, incloent-hi l'històric.
  En el teu Proxmox també pots fer una còpia/snapshot de la VM aturada.
- Si proves una VM clonada, no deixis les dues instàncies parlant al mateix
  descalcificador: atura la integració/Core de producció o bloqueja l'accés del
  clon a l'aparell.
- Anota les versions de HA, HACS i la integració. Desa captures dels IDs i noms
  d'entitats, opcions, dispositiu, historial i dashboards abans del canvi.
- Atura les actualitzacions automàtiques de HACS per a aquesta integració durant
  la prova. No la reinstal·lis, eliminis o descarreguis des de HACS a mig procés.
  L'eina no modifica la configuració interna de HACS.
- Necessites un terminal que continuï funcionant amb Core aturat, Python 3.10+
  i git. En HA OS pot ser l'add-on de terminal/SSH. No cal instal·lar llibreries
  Python. Si falten Python/git, identifiquem primer quin add-on utilitzes.

Comprovacions inicials:

```sh
python3 --version
git --version
ha core info
```

Els exemples assumeixen que la configuració real de HA és `/config` i que pots
escriure a `/share`. Alguns add-ons exposen la configuració com `/homeassistant`:
si és així, substitueix `/config` en totes les ordres. La carpeta correcta conté
`.storage/core.config_entries`; no enganxis el contingut d'aquest fitxer.

```sh
git clone --depth 1 --branch feat/runxin-domain-migration https://github.com/Danirv/runxin-local.git /share/runxin-domain-pilot
python3 /share/runxin-domain-pilot/scripts/migrate_domain.py preview --config-dir /config
```

**Preview no canvia res.** Mostra quantitats d'entrades, entitats, dispositius i
informes. No mostra IPs, MACs ni credencials. Si rebutja la migració, revisem-ne
el motiu; no eliminis ni tornis a donar d'alta dispositius per forçar-la.

## 2. Migrar amb Core aturat

Primer comprovem el resultat de preview i que la còpia completa és recuperable.
Després:

```sh
ha core stop
ha core info
python3 /share/runxin-domain-pilot/scripts/migrate_domain.py apply --config-dir /config --core-stopped
```

Confirma que Core s'ha aturat. `--core-stopped` és la teva confirmació explícita:
l'eina no pot verificar aquest estat entre contenidors ni aturar Core per tu.

L'eina desa els originals i el diari de la transacció en una carpeta privada
`/config/runxin-domain-backup-<data>-<sufix>`. Conserva allí el codi antic, instal·la
`runxin_local` i traspassa els registres. Comprova conflictes i canvis concurrents.
Si hi ha un error gestionat, restaura els originals; si el procés s'interromp,
el diari permet intentar recuperar-los. No hi ha una única operació atòmica per
als múltiples fitxers.

**No comparteixis aquesta carpeta:** la còpia del registre conté també configuració
i possibles secrets d'altres integracions. No substitueix la còpia completa de HA.

Si acaba correctament, copia la ruta exacta que imprimeix i verifica abans
d'arrencar. Substitueix la ruta d'exemple; no escriguis els signes `<` i `>`.

```sh
python3 /share/runxin-domain-pilot/scripts/migrate_domain.py verify --backup-dir /config/runxin-domain-backup-<data>-<sufix>
ha core start
```

Si hi ha un error, deixa Core aturat fins a recuperar una combinació coherent de
registres i codi. No improvisis modificacions de `.storage`.

## 3. Comprovar el teu G6

1. Mateixos IDs de configuració, entitats i dispositiu; cap duplicat ni entitat
   nova amb `_2`. Mateixos noms, àrees, etiquetes i entitats desactivades.
2. Lectures i unitats normals; històric i estadístiques visibles amb els IDs antics.
3. Mateixes opcions de sondeig i sincronització del rellotge. Quan arrenqui Core,
   es reprèn el comportament habitual de la integració, incloses les opcions
   activades; la migració no envia ordres al dispositiu.
4. Dashboards i automatitzacions resolen les entitats de sempre. Revisa les
   referències explícites al domini i els loggers antics.
5. Els serveis `ypsilon_local.write_fields` i `ypsilon_local.advance_phase`
   continuen registrats. No cal iniciar una regeneració per provar-los.
6. Si ja tenies una entrada de diagnòstic, encara pots descarregar el mateix informe
   sense controls ni lectures addicionals.
7. Reinicia Core una segona vegada i repeteix la comprovació d'IDs i duplicats.
   Revisa els logs d'errors de configuració o d'integració absent.

Després que HA hagi desat els registres, repeteix `verify` amb la mateixa ruta.
Comprova els IDs i les preferències; no valida l'històric físicament, les referències
YAML, el comportament del controlador ni HACS. Si un resultat és ambigu mentre
Core desa asíncronament, repetim la verificació després d'una aturada neta.

Comparteix les versions, les quantitats de preview/verify, captures anonimitzades
abans/després i errors sense dades privades. **No comparteixis els registres ni
les còpies.** Provar el G6 no valida el model 12 o altres versions de HA.

## 4. Tornar enrere

Abans d'haver posat en marxa Core, o per recuperar una aplicació interrompuda:

```sh
ha core stop
python3 /share/runxin-domain-pilot/scripts/migrate_domain.py rollback --backup-dir /config/runxin-domain-backup-<data>-<sufix> --core-stopped
ha core start
```

Rollback verifica les còpies i rebutja sobreescriure canvis posteriors de registres
o codi. Si ja has arrencat el pilot i ho rebutja, **restaura la còpia completa de
HA o la VM anterior**. No forcis canvis ni substitueixis només la carpeta del codi.

La PR continua en esborrany fins que confirmem la prova real i la recuperació.
Abans de publicar una versió estable també cal provar per separat que HACS refresca
el domini del repositori i gestiona les actualitzacions sense recrear entrades,
eliminar la carpeta incorrecta o deixar dos dominis actius. Consulta també la
[guia completa en anglès](domain-migration.md).
