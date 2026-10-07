# Seguimiento de arquitectura y documentación — 08/10/2026

[English](audit-followup.md) | [Català](audit-followup.ca.md) | [Español](audit-followup.es.md)

Continúa la auditoría del conjunto tras la PR #25 y **2.9.0-alpha.1**, desde main `036b808`. La [auditoría inicial](multi-model-audit.md) recoge la implementación Alpha; aquí se siguen los pendientes comunes. Se excluye la PR #21 y la migración permanece separada en la PR #24.

La estructura transporte / protocolo puro / adaptador / política de modelo / HA es adecuada. Los modelos comparten el códec cuando los datos lo demuestran y solo incorporan diferencias contrastadas de unidades, permisos o aplicabilidad. No hace falta duplicar carpetas. Una familia distinta necesitará descriptor, catálogo, fixtures y selección propios; `protocol_profile` sigue siendo metadato descriptivo.

## Mejoras aplicadas

- Auditoría recursiva de imports: detecta salidas del paquete puro mediante imports relativos, dependencias de red y acoplamiento al transporte. Los transportes no pueden importar catálogos/semántica ni el adaptador HA; errores y tramas neutrales son admisibles.
- Diagnósticos con `write_policy`: identidad configurada/observada, bloqueo del coordinador/adaptador, intersección de campos permitidos y reloj solicitado/permitido. La evidencia del modelo permanece separada. La exportación solo consulta memoria caché.
- Suite completa con HA 2026.9.3 y 2026.9.4, Python 3.14 y herramientas fijadas. No se declara una versión mínima de HA.
- Fuentes checkout/setup-python/HACS/hassfest fijadas a commits; la auditoría rechaza referencias flotantes. Dependabot mantiene sus actualizaciones semanales.
- Guías EN/CA/ES de contribución/publicación alineadas con las pruebas completas, prereleases, marca Runxin Local y política compartida.

**Límite de CI:** los descriptores HACS/hassfest todavía ejecutan contenedores con tags flotantes. Fijar su fuente no fija las imágenes ni todas las dependencias transitivas. La auditoría de imports es estática, no un sandbox.

Se conservan códecs, conversiones/rangos G6/modelo 12, tramas, lecturas, dominio, config-entry v2 y unique IDs. No se habilitan comandos nuevos. Los cambios runtime solo añaden metadatos de diagnóstico.

## Pendientes concretos

| Punto | Qué falta | Próximo paso |
|---|---|---|
| Modelo 1 | Unidades/etiquetas de la app y lecturas cercanas; primero resina 240 y cantidad por ciclo 15 | Comparaciones de la issue #17 y corrección/fixture propia; sin multiplicadores supuestos ni controles. |
| Modelo 12 | Campos 7/47/34 y funcionamiento sostenido | Validación del propietario según la guía de hardware; Alpha actual intacta. |
| G6 mecánica/vacaciones | Comportamiento físico del campo 34 y acción local de vacaciones demostrada | Trabajo de hardware separado; campo 49 excluido. |
| Modelo 14/otros | Informes coherentes y comparaciones; IDs/códecs locales para campos adicionales | Solo diagnóstico. Las propiedades cloud no identifican campos locales superiores al 52. |
| Migración | Piloto HA con copia, registros/automatizaciones, camino HACS y actualización con main | Continuar la PR #24 separadamente cuando el mantenedor pueda probarla. |
| HA anteriores | Un objetivo anterior concreto y pruebas nativas | Solo se han probado 2026.9.3/2026.9.4; no prometer soporte anterior ni fijar un mínimo sin evidencia. |
| Contenedores de validación | Digests compatibles y un proceso de actualización | Revisión posterior; continuar la validación upstream. |
| Librería separada | Segundo consumidor real y contrato de distribución/versionado | Mantener el paquete puro aquí hasta que se justifique. |

El campo 52 sigue en caché independiente y puede ser anterior al resto. Recibir cero/false no demuestra aplicabilidad física.

## Validación y publicación

Usa entornos separados con `requirements-test-offline.txt`, `requirements-test-ha.txt` y `requirements-test-ha-baseline.txt` y ejecuta `python -m pytest -q` en cada uno. Consulta [CONTRIBUTING](../CONTRIBUTING.es.md) para publicación, auditoría, cobertura de campos y compilación. Las pruebas simulan E/S y no sustituyen hardware.

Este mantenimiento es **Unreleased**: no mueve ni reemplaza el tag Alpha publicado. Hace falta una versión nueva conjunta de manifest/changelog/info antes de distribuirlo. El mantenedor decide la fusión/publicación.

Resultados locales: **275 pruebas superadas con cada versión de HA**, **136 superadas / 3 módulos HA omitidos** offline, además de publicación, arquitectura, campos, YAML/shell, enlaces relativos, diff y compilación. HA emite un aviso upstream de deprecación de aiohttp. Los checks finales de GitHub constan en la PR.
