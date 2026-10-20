# Install, configure and update Runxin Local

[English](installation.md) | [Català](installation.ca.md) | [Español](installation.es.md) · [Documentation](index.md)

## Before installation

Use **Home Assistant 2026.10.0+**, a reachable BL3372 module (`0x520F`) and a controller listed in the [support matrix](model-support.md). HACS declares the minimum HA version in `hacs.json`. Home Assistant installs `broadlink-async>=1.1.0`; do not install packages into its managed environment yourself.

For older HA versions, keep Runxin Local 2.9.3. Before updating an installation that used the shared BroadLink dependency, consult [migration and recovery](ha-2026-10.md).

## HACS installation

Runxin Local is in the [HACS default catalog](https://github.com/hacs/default/pull/10717).

1. With [HACS configured](https://www.hacs.dev/docs/use/), open HACS and search for **Runxin Local**.
2. Open the repository and download the integration.
3. Restart Home Assistant.
4. Continue with device setup below. Downloading the files does not configure the softener.

New catalog entries can take up to eight hours to appear after acceptance. If the entry is not yet visible, wait for HACS metadata to refresh; the project was accepted on 20 October 2026. Existing custom-repository installations can continue updating the same repository without reinstalling the device.

## Manual installation

1. Download the integration ZIP from a [published release](https://github.com/Danirv/runxin-local/releases).
2. Back up an existing `custom_components/ypsilon_local` folder before replacing its files.
3. Place the ZIP's **`custom_components/ypsilon_local`** folder at **`/config/custom_components/ypsilon_local`**. Do not introduce another nested `custom_components` folder or rename it to `runxin_local`.
4. Restart Home Assistant and continue with device setup.

## Device setup

Open **Settings → Devices & services → Add integration → Runxin Local**, enter the local IP address and follow the form. The device must be reachable from HA on the LAN. Reserving its address in DHCP helps keep it stable.

Automatic discovery uses BroadLink MAC prefixes as hints, then checks the module type and controller identity. Other BroadLink types are discarded before authentication; a BL3372 with a connection problem or an unknown Runxin model can offer diagnostics. Discovery never establishes compatibility merely from the MAC prefix.

Model 1 has an additional explanation of its Beta readings, uncertain units and manual clock controls. Its default polling is once a minute, with adaptive polling and automatic clock correction off. See [model 1](models/model-1.md).

If you previously saved a **diagnostic-only entry**, download its report and delete that diagnostic entry before adding the same device normally. A diagnostic entry has no operational entities and is not automatically converted into a normal entry.

## Updating an existing installation

Update through HACS, or replace the integration files for a manual installation, then restart HA. Keep existing operational entries, entity IDs and automations. The project rename and HACS acceptance do not require re-pairing or removing the integration.

The current domain, folder and service prefix remain **`ypsilon_local`**. A future domain migration is separate work. To change a configured device's IP address, use its **Reconfigure** flow rather than creating a duplicate entry.

A normal update to the isolated dependency does not itself require rebuilding Core. Already damaged BroadLink dependencies on HA 2026.10.0/1 have a separate [recovery procedure](ha-2026-10.md#upgrade-and-recovery).

## After setup

Check the [model-specific policy](model-support.md), [entities and water statistics](usage.md) and [polling options](usage.md#polling-and-clock-options). If setup fails, use [troubleshooting](troubleshooting.md) or the [built-in read-only report](compatibility-report.md); editing the model registry is not required for a report.
