# crypto-steganography roadmap

Written 2026-10-30 from the repo as it stands. No dates on the future
items, because I do not know when I will be back in this code, and a
date I invent here would be a small lie in a public file.

## Done

- Hide: random salt per run, PBKDF2-HMAC-SHA256 key derivation at
  390000 iterations, Fernet encryption, and the three segment LSB
  layout (salt, length, payload) written by _write_bits.
- Extract: _read_bits reads the segments back in the same order, the
  length is checked before it is trusted, the key is rebuilt from
  the stored salt, and the message prints only if decryption works.
- The fixes that made the numbers honest: the capacity check counts
  the 160 bit header, output is always PNG, Pillow is in
  requirements.txt, failed hides and extracts exit 1, and the two
  directions share one pair of bit loops instead of carrying copies.
- A README that states the capacity math and the JPEG warning in
  plain words, and these visuals.

## Working now

- Nothing in flight. The repo is in a finished, working state as of
  the 2026-10-30 campaigns.

## Next

- A test file for the round trip: hide a known message into a known
  image, extract it, compare. Right now the README records a hand
  verification and nothing in the repo can re-run it.
- Nothing else is queued. The code has no TODO or FIXME markers in
  it (checked 2026-10-30), so this section stays short on purpose.

## Later

- Reading the message from a file instead of the command line would
  suit longer texts, but the command line argument is the interface
  I actually use, so it waits until I need it.

## Not planned

- Hiding whole files or binary data. The segment layout is built
  around a Fernet token from a text message, and growing it into a
  file format is a different tool.
- A graphical interface. Two subcommands and three arguments are
  the whole surface, and a window around that adds nothing.
