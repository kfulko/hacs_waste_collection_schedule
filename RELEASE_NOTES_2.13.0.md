# 2.13.0

## Core Changes

- **Replace cloudscraper with curl_cffi**: Switched anti-bot scraping library from cloudscraper to curl_cffi with Chrome impersonation across 10+ sources for improved reliability (#5720)
- Fixed AttributeError on startup when YAML_CONFIG is absent from hass.data (#5701)
- Fixed translation placeholder mismatch causing HA startup errors for Bridgend, Cumberland, and Dartford sources (#5700)
- Replaced PyMuPDF with pdfminer.six/pypdf for PDF extraction to fix aarch64 installation failures (#5710)

## Added Sources

- added City of Kalamunda, WA, AU (thanks @Brodiemm) (#5566)
- added Watford Borough Council, UK (thanks @Cironni) (#5629)
- added City of Moonee Valley, VIC, AU (thanks @mvandersteen) (#5285)
- added Midlothian Council, Scotland, UK (thanks @vivekxp) (#5640)
- added Memotri - Agglomeration Pau Bearn Pyrenees, FR (thanks @vchatela) (#5620)

## Fixed Sources

- fixed Muellmax, DE: restored two-step street search, fixed session handling and duplicate key issues (#5702)
- fixed Rushcliffe, UK: handle address list format change and POST_ARGS mutation (#5672, #5717)
- fixed Gateshead, UK: 403 error resolved by switching to curl_cffi (#5706)
- fixed South Kesteven, UK: updated to use current selfservice endpoint (thanks @CraigBell) (#5505)
- fixed Christchurch (ccc_govt_nz), NZ: stale API dates causing missing collections (#5645)
- fixed Grafikai Svara, LT: GUI config returning empty response (#5646)
- fixed AHK Heidekreis, DE: handle API field name changes robustly (#5692)
- fixed Tauranga, NZ: updated API URLs and improved form field discovery (thanks @samwalshnz) (#5610)
- fixed Melton, VIC, AU: refactored date parsing and validation (thanks @viperaus) (#5715)

## Improved Sources

- improved AWIDO, DE: added location and time attributes for Schadstoffmobil events (#5685)
- improved EcoHarmonogram, PL: added configurable language parameter (#5649)
- improved Wealden, UK: added food waste collections (thanks @ryanbdclark) (#5688)
- improved mijnblink/HVCGroep, NL: moved to Ximmio service (thanks @xesxen) (#5707)

## New Contributors

Welcome to the following first-time contributors! :tada:

@Brodiemm, @Cironni, @CraigBell, @mvandersteen, @ryanbdclark, @samwalshnz, @vchatela, @vivekxp, @viperaus, @xesxen
