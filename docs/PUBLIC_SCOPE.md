# Public scope

This is the standalone open-source demo of Ludus. Its code is released under MIT. The private launcher and separately operated Ludus services are not part of this repository. The demo has its own code and repository history. The full launcher is not open source, and this repository is not its complete implementation.

The sample catalogue is static, fictional data stored in `data/games.json`. Game descriptions and generated covers require no online artwork services.

The public backend serves its allowlisted interface files, catalogue and sample downloads. aria2 can download only the included samples from the local server. It does not accept external URLs, install games or run downloaded files.

Library, profile and appearance data are local browser preferences. JSON export is a manual local backup, not a cloud save. Import keeps known game IDs and supported fields, with length limits. It does not execute imported content.

No credentials, databases, production service integrations or original Git history are included. There is no production SDK, undocumented service connector or private launcher module. Public development should use fictional fixtures and local behaviour.

Other motors in the full app: libtorrent and Ryuu.
