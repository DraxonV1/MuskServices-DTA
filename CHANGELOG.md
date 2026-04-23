# MuskDTA CLI Changelog

## v1.1.0 (for Gen v9.0.0)

- Added **AFK mode** in setup and quick mode switching.
- Launcher header now shows the live release version dynamically.
- Fixed repeated `pillow` missing/install loop.
- Simplified setup by removing the HTTP library prompt.
- Added extension storage paths in CLI data folder:
  - `~/.muskdta/extensions/nopecha_ext`
  - `~/.muskdta/extensions/proxy_extension`
- Added diagnostics and utility commands:
  - `muskdta doctor`
  - `muskdta config validate`
  - `muskdta mode set <worker|private|afk>`
  - `muskdta extensions sync`
  - `muskdta logs --lines N`
- Existing configs now auto-upgrade with latest required fields.

## User Notes

- Run `muskdta config` once after update.
- If you already had config before, launching once auto-syncs missing fields.
