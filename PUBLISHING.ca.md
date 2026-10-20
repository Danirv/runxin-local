# Publicar Runxin Local

[English](PUBLISHING.md) | [Català](PUBLISHING.ca.md) | [Español](PUBLISHING.es.md)

Runxin Local forma part del catàleg de HACS des de [hacs/default#10717](https://github.com/hacs/default/pull/10717), fusionat el 20 d’octubre de 2026. Les releases continuen en aquest repositori; no cal una sol·licitud d’inclusió per cada versió. El suport per model i el canal de release són independents.

<a id="1-metadades-del-repositori"></a>
<a id="2-requisits-del-repositori"></a>
<a id="3-publicar-una-github-release-des-de-la-web"></a>
<a id="4-provar-mitjançant-hacs"></a>
<a id="5-inclusió-per-defecte-a-hacs"></a>
<a id="disciplina-de-release"></a>
<a id="prereleases-i-manteniment"></a>
<a id="publicar-runxin-local-a-github-i-hacs"></a>

## Preparar una release

1. Tria una versió semàntica nova i no utilitzada. No reutilitzis ni moguis un tag publicat per distribuir codi posterior.
2. Actualitza conjuntament `manifest.json`, `CHANGELOG.md` i el títol/resum actual d’`info.md`. L’historial anterior queda al changelog.
3. Executa les comprovacions de sota a l’entorn offline i les suites HA completes en entorns separats amb `requirements-test-ha.txt` i `requirements-test-ha-baseline.txt`.
4. Fusiona a `main` quan passin HACS, hassfest, auditories i regressions HA.

El manteniment només de documentació es pot fusionar sense canviar manifest ni publicar una release.

## Publicar des de GitHub

1. Obre **Actions → Publish GitHub release → Run workflow**.
2. Selecciona **main** i executa’l.
3. Comprova release, tag `v<versió del manifest>`, ZIP d’instal·lació manual i validacions.

El workflow llegeix la versió, executa comprovacions offline de publicació/auditoria/camps/tests/compilació, rebutja una GitHub Release existent, crea o recupera el tag anotat, valida exactament el codi etiquetat, construeix el ZIP i publica. No substitueix les proves natives HA prèvies al merge.

Una versió amb `-` es publica com a `--prerelease --latest=false`. L’estat Alpha/Beta d’un model no converteix per si sol la release en prerelease ni modifica permisos.

## Alternativa amb Git

```bash
VERSION="$(python -c 'import json; print(json.load(open("custom_components/ypsilon_local/manifest.json"))["version"])')"
git tag -a "v${VERSION}" -m "Runxin Local ${VERSION}"
git push origin "v${VERSION}"
```

## Comprovacions i manteniment

```bash
python scripts/docs_check.py
python scripts/publication_check.py
python scripts/audit.py
python scripts/field_surface_audit.py
python -m pytest -q
python -m compileall -q custom_components/ypsilon_local scripts tests
```

No creïs una release duplicada per al mateix tag. Un tag pujat manualment activa el job de tags; el job web completa la seva release sense necessitar una altra execució.

Mantén Issues, temes, marques, revisions d’accions i validacions HACS/hassfest. El canvi de nom ja fet es documenta a [instal·lació](docs/installation.ca.md); no reutilitzis el nom antic de GitHub i conserva `ypsilon_local`.

`scripts/configure_repository.py` serveix per adaptar una plantilla/fork nou, no per publicar rutinàriament. No pugis APK, firmware, volcats propietaris, credencials, claus ni captures sense sanejar. [Contribuir](CONTRIBUTING.ca.md) i [mantenir documentació](docs/documentation.md).
