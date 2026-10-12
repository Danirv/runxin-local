# Third-party software

Runxin Local depends on `python-broadlink>=1.0.6`, the MIT-licensed [DAB-LABS/python-broadlink](https://github.com/DAB-LABS/python-broadlink) fork of [mjg59/python-broadlink](https://github.com/mjg59/python-broadlink). Home Assistant installs the distribution; it is not vendored here. Its import name remains `broadlink`, so the old `broadlink` distribution must not be installed in the same environment.

`transport/broadlink_packet.py` adapts the tested library’s framing/endpoint interface to enforce one-datagram writes and strict BL3372 replies. It does not patch global classes or redistribute the library. Its private-API assumptions are covered by tests against 1.0.6; a dependency upgrade must revalidate them.

Home Assistant and HACS are separate projects with their own licenses and trademarks. No vendor firmware or application binaries are redistributed here.
