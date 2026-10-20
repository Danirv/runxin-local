# Publicar Runxin Local

[English](PUBLISHING.md) | [Català](PUBLISHING.ca.md) | [Español](PUBLISHING.es.md)

Runxin Local forma parte del catálogo de HACS desde [hacs/default#10717](https://github.com/hacs/default/pull/10717), fusionado el 20 de octubre de 2026. Las releases continúan en este repositorio; no hace falta una solicitud de inclusión por versión. El soporte por modelo y el canal de release son independientes.

<a id="1-metadatos-del-repositorio"></a>
<a id="2-requisitos-del-repositorio"></a>
<a id="3-publicar-una-github-release-desde-la-web"></a>
<a id="4-probar-mediante-hacs"></a>
<a id="5-inclusión-por-defecto-en-hacs"></a>
<a id="disciplina-de-release"></a>
<a id="prereleases-y-mantenimiento"></a>
<a id="publicar-runxin-local-en-github-y-hacs"></a>

## Preparar una release

1. Elige una versión semántica nueva y no utilizada. No reutilices ni muevas un tag publicado para distribuir código posterior.
2. Actualiza conjuntamente `manifest.json`, `CHANGELOG.md` y el título/resumen actual de `info.md`. El historial anterior queda en el changelog.
3. Ejecuta las comprobaciones de abajo en el entorno offline y las suites HA completas en entornos separados con `requirements-test-ha.txt` y `requirements-test-ha-baseline.txt`.
4. Fusiona en `main` cuando pasen HACS, hassfest, auditorías y regresiones HA.

El mantenimiento solo de documentación puede fusionarse sin cambiar el manifiesto ni publicar una release.

## Publicar desde GitHub

1. Abre **Actions → Publish GitHub release → Run workflow**.
2. Selecciona **main** y ejecútalo.
3. Comprueba release, tag `v<versión del manifiesto>`, ZIP de instalación manual y validaciones.

El workflow lee la versión, ejecuta comprobaciones offline de publicación/auditoría/campos/tests/compilación, rechaza una GitHub Release existente, crea o recupera el tag anotado, valida exactamente el código etiquetado, construye el ZIP y publica. No sustituye las pruebas nativas HA previas al merge.

Una versión con `-` se publica como `--prerelease --latest=false`. El estado Alpha/Beta de un modelo no convierte por sí solo la release en prerelease ni modifica permisos.

## Alternativa con Git

```bash
VERSION="$(python -c 'import json; print(json.load(open("custom_components/ypsilon_local/manifest.json"))["version"])')"
git tag -a "v${VERSION}" -m "Runxin Local ${VERSION}"
git push origin "v${VERSION}"
```

## Comprobaciones y mantenimiento

```bash
python scripts/docs_check.py
python scripts/publication_check.py
python scripts/audit.py
python scripts/field_surface_audit.py
python -m pytest -q
python -m compileall -q custom_components/ypsilon_local scripts tests
```

No crees una release duplicada para el mismo tag. Un tag subido manualmente activa el job de tags; el job web completa su release sin necesitar otra ejecución.

Mantén Issues, temas, marcas, revisiones de acciones y validaciones HACS/hassfest. El cambio de nombre ya realizado se documenta en [instalación](docs/installation.es.md); no reutilices el nombre antiguo de GitHub y conserva `ypsilon_local`.

`scripts/configure_repository.py` sirve para adaptar una plantilla/fork nuevo, no para publicar rutinariamente. No subas APK, firmware, volcados propietarios, credenciales, claves ni capturas sin sanear. [Contribuir](CONTRIBUTING.es.md) y [mantener documentación](docs/documentation.md).
