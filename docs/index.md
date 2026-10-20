# Runxin Local documentation

[Project overview](../README.md) · [Català](README.ca.md) · [Español](README.es.md)

Use the task sections below. Installation and usage describe current behavior; the support matrix records current model policy; research pages preserve dated observations and their limits. Release chronology belongs in the changelog.

## Install and use

| Task | English | Català | Español |
|---|---|---|---|
| Install, configure, update | [Installation](installation.md) | [Instal·lació](installation.ca.md) | [Instalación](installation.es.md) |
| Entities, water statistics, salt, polling, controls | [Usage](usage.md) | [Ús](usage.ca.md) | [Uso](usage.es.md) |
| Diagnose discovery or authentication | [Troubleshooting](troubleshooting.md) | [Connexió](troubleshooting.ca.md) | [Conexión](troubleshooting.es.md) |
| Recover older BroadLink dependencies | [HA 2026.10 migration](ha-2026-10.md) | [Migració](ha-2026-10.ca.md) | [Migración](ha-2026-10.es.md) |
| Unknown controller or failed setup | [Built-in read-only report](compatibility-report.md) | English reference | English reference |

## Choose a controller guide

The [support matrix](model-support.md) is the single current policy summary for all controllers, including the reference **9 / F79D / Ypsilon G6**. It distinguishes enabled writes, confirmed writes, pending conversions and hardware scope.

| Controller | English | Català | Español |
|---|---|---|---|
| 1 / F150 API name | [Model 1](models/model-1.md) | [Model 1](models/model-1.ca.md) | [Modelo 1](models/model-1.es.md) |
| 12 / F105 / Midnight | [Model 12](models/model-12.md) | [Model 12](models/model-12.ca.md) | [Modelo 12](models/model-12.es.md) |
| 14 / F136 / Midnight | [Model 14](models/model-14.md) | [Model 14](models/model-14.ca.md) | [Modelo 14](models/model-14.es.md) |

## Develop and extend

| Task | English | Català | Español |
|---|---|---|---|
| Development environment and checks | [Contributing](../CONTRIBUTING.md) | [Contribuir](../CONTRIBUTING.ca.md) | [Contribuir](../CONTRIBUTING.es.md) |
| Layers, responsibilities and invariants | [Architecture](architecture.md) | [Arquitectura](architecture.ca.md) | [Arquitectura](architecture.es.md) |
| Add a compatible controller or new profile | [Device profiles](adding-a-device-profile.md) | [Perfils](adding-a-device-profile.ca.md) | [Perfiles](adding-a-device-profile.es.md) |
| Add another communication module | [Transports](adding-a-transport.md) | [Transports](adding-a-transport.ca.md) | [Transportes](adding-a-transport.es.md) |
| Release workflow and maintenance | [Publishing](../PUBLISHING.md) | [Publicar](../PUBLISHING.ca.md) | [Publicar](../PUBLISHING.es.md) |
| Keep documentation consistent | [Documentation maintenance](documentation.md) | English reference | English reference |

## Protocol reference and evidence

| Reference | English | Català | Español |
|---|---|---|---|
| Framing, opcodes and evidence model | [Protocol](protocol.md) | [Protocol](protocol.ca.md) | [Protocolo](protocol.es.md) |
| Field catalogue, codecs and units | [F79D](f79d.md) | [F79D](f79d.ca.md) | [F79D](f79d.es.md) |
| Recovered enums and setting ranges | [Settings](f79d-settings.md) | [Ajustos](f79d-settings.ca.md) | [Ajustes](f79d-settings.es.md) |
| BL3372 sessions, packets and delivery | [BroadLink transport](broadlink-bl3372.md) | [Transport](broadlink-bl3372.ca.md) | [Transporte](broadlink-bl3372.es.md) |
| Physical read/write validation by model | [Hardware evidence](hardware-verification.md) | [Verificació](hardware-verification.ca.md) | [Verificación](hardware-verification.es.md) |
| Dated model-1 comparisons and operation | [Model-1 record](evidence/model-1.md) | [Registre](evidence/model-1.ca.md) | [Registro](evidence/model-1.es.md) |
| Legacy WaterDevice investigation | [Research](waterdevice-audit.md) | [Recerca](waterdevice-audit.ca.md) | [Investigación](waterdevice-audit.es.md) |

The English field catalogue is the complete reference; some translated technical pages are condensed. Translated operational guidance must agree on versions, units, permissions and known limitations. A cloud enum, received field or theoretical write codec does not establish physical support.

## Project policies and history

| Topic | English | Català | Español |
|---|---|---|---|
| Release history | [Changelog](../CHANGELOG.md) | English reference | English reference |
| Security reports | [Security](../SECURITY.md) | [Seguretat](../SECURITY.ca.md) | [Seguridad](../SECURITY.es.md) |
| Interoperability and trademarks | [Legal](../LEGAL.md) | [Nota legal](../LEGAL.ca.md) | [Nota legal](../LEGAL.es.md) |
| Dependency attribution | [Third-party dependencies](../THIRD_PARTY.md) | English reference | English reference |
| Community behavior | [Code of conduct](../CODE_OF_CONDUCT.md) | English reference | English reference |
| License and notice | [Apache 2.0](../LICENSE), [NOTICE](../NOTICE) | Same license | Same license |

The `model-*-alpha*.md` pages are compatibility entry points for previously shared links. New links use `models/`; those older paths do not define current support status. The integration domain remains `ypsilon_local`.
