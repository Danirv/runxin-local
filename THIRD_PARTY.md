# Third-party dependencies

Runxin Local 2.10.1 depends on `broadlink-async>=1.1.0`, the MIT-licensed [DAB-LABS/broadlink-async](https://github.com/DAB-LABS/broadlink-async) fork of [mjg59/python-broadlink](https://github.com/mjg59/python-broadlink). Home Assistant installs the distribution; it is not vendored here. It imports as `broadlink_async`, separately from the legacy `broadlink` distribution and the superseded `python-broadlink` 1.0.6 distribution. Core BroadLink uses this isolated namespace from HA 2026.10.2.

`transport/broadlink_packet.py` adapts the library’s framing/endpoint interface to enforce one-datagram writes and strict BL3372 replies. It does not patch global classes or redistribute the library. Its private-API assumptions are covered by real-library/AES/loopback tests against 1.1.0; a dependency upgrade must revalidate them. Dedicated coexistence tests install the real legacy 0.19.0 package alongside it; legacy BroadLink is not a Runxin runtime dependency.
