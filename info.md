# Runxin Local 2.10.3

Local Home Assistant integration for compatible Runxin controllers and BroadLink BL3372 Wi-Fi modules. Requires **Home Assistant 2026.10.0+**; normal operation uses the LAN without the vendor cloud.

## Install and configure

Runxin Local is in the HACS default catalog. Download it from HACS, restart Home Assistant, then open **Settings → Devices & services → Add integration → Runxin Local** and enter the device's local IP address. Keep existing operational entries when updating.

The integration folder and service domain remain `ypsilon_local`. Existing Ypsilon installations do not require removal, re-pairing or entity recreation.

## Supported hardware

- **9 / F79D:** reference ATH/BWT Ypsilon G6.
- **1 / F150 API name:** Beta readings, Energy-compatible daily consumption and validated manual clock; resin/per-cycle units are unconfirmed and other writes require opt-ins.
- **12 / F105:** Euro-Clear Midnight 25 / ECOPRO+, Beta.
- **14 / F136:** Euro-Clear Midnight 25 / ECOPRO+, Beta with confirmed model-specific resin decoding.

Verified writes and pending actions are separate from support labels. See the [support matrix](docs/model-support.md).

## Current release

**2.10.3** filters DHCP discoveries by BroadLink type `0x520F`, so RM remotes and SP plugs do not produce Runxin setup offers. Manual read-only diagnostics remain available. It retains the isolated `broadlink-async` dependency, model policies and existing identities.

Use **Daily consumption** for consumed-water statistics. Added salt is a controller setting, not measured salt remaining; vacation is read-only. See the [usage guide](docs/usage.md).

[Installation and updates](docs/installation.md) · [Connection help](docs/troubleshooting.md) · [Read-only compatibility report](docs/compatibility-report.md) · [All documentation](docs/index.md) · [Release history](CHANGELOG.md)
