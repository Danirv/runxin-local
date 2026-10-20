[English](protocol.md) | [Català](protocol.ca.md) | [Español](protocol.es.md) · [Documentation](index.md)

<a id="protocol-layering-and-evidence"></a>
<a id="field-codecs-and-field-7-evidence"></a>
<a id="vacation-semantics"></a>
<a id="waterstatistics-and-salt-semantics"></a>
<a id="field-52-polling"></a>
<a id="bl3372-envelope"></a>
<a id="compatibility-boundary"></a>

# Protocol framing and delivery

Home Assistant applies controller policy; the reusable F79D client builds and validates raw Runxin frames; the selected transport adds its own envelope and manages the device session. See [architecture](architecture.md) for module responsibilities.

## Raw F79D frame

The observed outer frame starts `5A 5C` and ends `A5`; its inner frame starts `DF FD` and ends `DE`. Both have additive 8-bit checksums. Field values are triples `[field_id, byte_1, byte_2]`.

| Operation | Request opcode | Reply opcode |
|---|---|---|
| Read fields | `0x09` | `0xC9` |
| Write fields | `0x19` | `0xD9` |

There is no global byte order. The [F79D catalogue](f79d.md) defines codecs, paired-volume rules and units. Field 7 is BE on the tested G6 despite a conflicting legacy-app interpretation; the [physical evidence](hardware-verification.md#field-7--flow-cutoff-evidence) records why. Controller-specific conversions and permissions are in the [support matrix](model-support.md).

## Evidence model

| Label | Meaning |
|---|---|
| `legacy_app_codec` | Recovered application representation |
| `device_state_observed` | Value/behavior observed in controller data |
| `hardware_write_verified` | Local command followed by an independent fresh read and physical/semantic confirmation |
| `cloud_write_observed` | Change observed through the vendor path |
| `inferred` | Interpretation not independently confirmed |

These labels do not grant integration write permissions. An ACK alone is not physical evidence. [Hardware verification](hardware-verification.md) describes validation procedure and per-model results; [WaterDevice research](waterdevice-audit.md) separates legacy behavior from current-firmware acceptance.

## Read and write delivery semantics

Reads are idempotent and may use bounded retries. For a write, the transport sends the command once; a timeout, lost response or outer error after submission is ambiguous. The coordinator performs a fresh GET and reconciles state without blindly replaying the command. A mechanical action additionally requires the expected phase transition.

Only a fresh device reading can confirm that a setting matches the requested value; cached coordinator state cannot. The [BL3372 transport](broadlink-bl3372.md) documents authentication, reply validation, endpoint cleanup and retry budgets. Its two-byte LE length prefix, encryption and BroadLink command `0x6A` are outside the raw Runxin contract.

## Home Assistant policy versus codec capability

The codec can encode more fields than HA exposes. Administrator `write_fields` permits only allowed reversible settings and validates ranges/units; mechanical field 34 is handled separately. Field 49 remains readable/encodable for research but has no HA writer because its direct local write failed physical confirmation on the reference G6.

[Usage](usage.md) owns user-facing statistics, salt and vacation descriptions. Normal fields 1–51 and separately cached field 52 are polling policy in the composition adapter, not a universal protocol limit. A new controller or transport requires [profile evidence](adding-a-device-profile.md), not an assumption from a shared brand or module type.
