# Runxin Local for Home Assistant

[English](README.md) | [Català](docs/README.ca.md) | [Español](docs/README.es.md)

Local monitoring and control for water softeners with compatible **Runxin controllers** and a **BroadLink BL3372** Wi-Fi module. Normal operation communicates directly over your LAN and does not require the vendor cloud.

**Start here:** [Install and update](docs/installation.md) · [Supported models](docs/model-support.md) · [Using the integration](docs/usage.md) · [Troubleshooting](docs/troubleshooting.md) · [All documentation](docs/index.md)

<a id="model-and-protocol-policy"></a>
<a id="supported-hardware"></a>

## Requirements and compatibility

- **Home Assistant 2026.10.0 or later**. For older HA releases, retain Runxin Local 2.9.3 and read the [migration guide](docs/ha-2026-10.md) before updating HA.
- A reachable BroadLink **BL3372**, device type **`0x520F`**, and a supported controller model. A matching brand or MAC prefix alone does not establish compatibility.
- Runtime dependency: `broadlink-async>=1.1.0`, installed by Home Assistant in the isolated `broadlink_async` namespace.

| Controller | Reported hardware | Current support |
|---|---|---|
| 9 / F79D | ATH/BWT Ypsilon G6 | Reference hardware |
| 1 / F150 API name | Unbranded unit from issue #17 | Beta readings and validated manual clock; other controls require explicit test options |
| 12 / F105 | Euro-Clear Midnight 25 / ECOPRO+ | Beta; verified and pending writes recorded separately |
| 14 / F136 | Euro-Clear Midnight 25 / ECOPRO+ | Beta; model-specific resin conversion confirmed |

The [support matrix](docs/model-support.md) records exact permissions, conversion limits and hardware evidence. Alpha/Beta labels describe individual models, not the integration's release channel. Other models can use the [read-only compatibility report](docs/compatibility-report.md); a manufacturer enum name does not automatically enable support.

<a id="hacs"></a>
<a id="installation"></a>
<a id="manual"></a>

## Install with HACS

Runxin Local is included in the **HACS default catalog**, accepted in [hacs/default#10717](https://github.com/hacs/default/pull/10717) on 20 October 2026.

1. Open **HACS**, search for **Runxin Local**, and download the integration.
2. Restart Home Assistant.
3. Open **Settings → Devices & services → Add integration → Runxin Local** and enter the softener's local IP address, or accept a compatible discovery.

See [installation and updates](docs/installation.md) for manual installation, existing entries, diagnostic-only entries and older BroadLink dependencies. Existing installations do not need to be removed or paired again just because the repository entered HACS.

<a id="advanced-services"></a>
<a id="entity-model"></a>
<a id="highlights"></a>
<a id="salt-semantics"></a>
<a id="state-verification-and-safety"></a>
<a id="vacation-status-read-only-by-design-in-261"></a>
<a id="water-dashboard"></a>
<a id="water-quantities-and-statistics"></a>
<a id="water-units-and-f79d-codec-notes"></a>

## What you can do

- Monitor flow, daily water consumption, remaining treatment capacity, operating status, regeneration settings and controller alerts.
- Add **Daily consumption** to Home Assistant's Energy dashboard as a water source. The weekly-average and per-cycle quantities have different meanings; see [water statistics](docs/usage.md#water-consumption-and-statistics).
- View diagnostic entities for phase durations, maintenance reminders, resin settings, controller identity and connection health.
- Use the settings and regeneration controls permitted by your model. Commands are reconciled against fresh device state; an ACK alone does not confirm a change.
- Export cached diagnostics or explicitly collect a bounded, read-only report for a new model or connection problem.

**Added salt amount is a controller setting, not a measured tank level. Vacation status is read-only.** The [usage guide](docs/usage.md) explains entities, polling, controls and advanced services. This integration can change settings and move the valve; it is not a certified safety controller or a replacement for independent leak protection.

## Existing Ypsilon installations

The project was renamed from **Ypsilon / ypsilon-local**. The Home Assistant domain, folder, service names and existing unique IDs remain **`ypsilon_local`**. Keep existing entries and automations. A future domain migration is separate work, not an installation step for this version.

<a id="branding"></a>
<a id="changelog"></a>
<a id="development"></a>
<a id="interoperability-and-legal-notice"></a>
<a id="reusing-the-protocol-work"></a>
<a id="sponsorship"></a>

## Help, development and project policies

| Need | Read |
|---|---|
| Connection or setup failure | [Troubleshooting](docs/troubleshooting.md) |
| Another controller model | [Compatibility report](docs/compatibility-report.md) |
| BroadLink dependency upgrade/recovery | [HA 2026.10 migration](docs/ha-2026-10.md) |
| Architecture, protocol, evidence and extensions | [Documentation index](docs/index.md) |
| Contribute or run checks | [CONTRIBUTING](CONTRIBUTING.md) |
| Publish a release | [PUBLISHING](PUBLISHING.md) |
| Release history | [CHANGELOG](CHANGELOG.md) |
| Security and interoperability | [SECURITY](SECURITY.md), [LEGAL](LEGAL.md), [THIRD_PARTY](THIRD_PARTY.md), [LICENSE](LICENSE) |

Community integration, independently developed for interoperability. Not affiliated with or endorsed by ATH, BWT, Runxin or BroadLink. No vendor application, firmware or credentials are distributed here. Optional funding links are configured through GitHub; funding does not change functionality or support priority.
