# SAMA 4.0.0-uat.2 release tooling

`import_authorities.py` performs a fresh, lossless import of the five authority
workbooks. Every source row carries workbook, worksheet, physical row, JSON
payload and SHA-256 provenance. Duplicate authority rows are preserved and
explicitly classified rather than silently dropped. The generated report is the
only source for release import totals; release counts are never constants.

Run the LAN package on the server with `START_SERVER.bat`, allow TCP port 8765 in
Windows Defender Firewall, and browse from LAN workstations to:

    http://SERVER-IP:8765
