# crypto-steganography, drawn out

I made these five pictures because the whole tool is one file,
main.py, and its one real idea, the three segment layout inside the
pixels, is easier to see drawn than to follow in prose. Everything in
them comes from main.py and the README beside it.

## The visuals

- [architecture.svg](architecture.svg): the system shape. One entry
  point, main(), a hide column and an extract column that mirror each
  other, and generate_key() across the bottom, the one function both
  directions share.
- [data-flow.svg](data-flow.svg): the hide path as data. Password and
  a fresh salt make the key, the key makes a Fernet token, and the
  token is written as three segments in a fixed order: salt (128
  bits), length (32 bits), payload, one bit per pixel.
- [flowchart.svg](flowchart.svg): a run, followed as decisions. Two
  lanes under one fork, and every failure in either lane ends the
  same way: a log line, no output, exit code 1.
- [product-map.svg](product-map.svg): the product in one frame, drawn
  around the picture itself: who it serves, what goes in, what comes
  out, and where it stops.
- [statistics.svg](statistics.svg): the numbers from the table below,
  drawn as bars on paper.

Each sheet also ships as a PNG beside its SVG (architecture.png,
flowchart.png, and so on): the same drawing, finished as a photograph
of the paper page.

Every sheet here is drawn to look like what it is: a page sketched by
hand on paper, and each one is signed GK somewhere in the drawing,
never twice in the same place, because that is what I do with a page
I made.

## Written product map

What it is: a command line tool that encrypts a short text with a
password, then hides the cipher text inside an image, one bit per
pixel, in the least significant bits. Extraction reads the bits back
and decrypts.

Who it serves: me, sending a short text that should not sit in plain
sight, and anyone who needs the same quiet trick on their own
machine.

Capabilities, grouped:

- Key making: a fresh 16 byte salt from os.urandom on every hide, and
  a 32 byte key derived from password and salt with
  PBKDF2-HMAC-SHA256 at 390000 iterations, base64 encoded for Fernet.
- Hiding: encrypt_message makes the Fernet token; _write_bits writes
  salt, length, and payload segments in that order, one bit per
  pixel, the channel cycling red, green, blue inside each segment
  and restarting at red for the next one.
- Extracting: _read_bits walks the same segments in the same order,
  rebuilds the salt, checks the length is sane, reads the payload,
  derives the key again, and decrypt_message opens the token.
- Guard rails in code: a capacity check before any pixel is touched
  (128 + 32 + payload bits must fit in width x height), a length
  sanity check on extract, and exit code 1 from main() whenever a
  hide or an extract returns nothing.

Inputs: for hide, an image file, the message, and a password. For
extract, the PNG the hide produced and the same password. Outputs:
one new PNG named hidden_<original base name>.png in the current
directory, or on extract the message printed as "Extracted message:
...".

Boundaries, what it does NOT do: text only, one image at a time. No
batch mode, no folder walk, no network use. The output is always
PNG, whatever went in, because a lossy format such as JPEG
recompresses the pixels and destroys the hidden bits. It does not
hide files, only text typed on the command line, and a wrong
password gets a logged decryption failure and no message.

## Statistics, with citations

Counted 2026-10-30, from the clone this folder ships in, at the
commit before this visuals set (c248ed4).

| Number | Value | How it was counted, and from what |
|---|---|---|
| Files in the repo | 6 | git ls-files in the clone, counted 2026-10-30 |
| Python lines | 240 | Line count over the 1 tracked .py file (main.py), by wc -l, 2026-10-30 |
| Markdown lines | 72 | Line count over the 1 tracked .md file (README.md), same method, 2026-10-30 |
| LICENSE lines | 21 | Line count over the tracked LICENSE file (no extension), same method, 2026-10-30 |
| Text lines | 2 | Line count over the 1 tracked .txt file (requirements.txt), same method, 2026-10-30 |
| Commits | 8 | git log in the clone, counted 2026-10-30 |
| First commit | 2025-03-28 | git log, oldest entry, 2026-10-30 |
| Last commit before this one | 2026-10-30 | git log, newest entry, 2026-10-30 |
| Tests | 0 test files; no suite run | No test file exists in the clone (git ls-files shows none), counted 2026-10-30. The README states the hide and extract round trip was verified by hand. I did not run the tool in this pass: the cryptography package is not installed in my sandbox, and main.py stops at its import. No pass is claimed. |
| Languages (API) | Python 8,576 bytes | GitHub API, GET /repos/ShadowGuard-AI/crypto-steganography/languages, read 2026-10-30 |
| Repo size (API) | 82 KB | GitHub API, GET /repos/ShadowGuard-AI/crypto-steganography, size field, read 2026-10-30 |
| Stars / forks (API) | 1 / 0 | Same API response, read 2026-10-30 |

External statistics: none. No outside number says anything honest
about this repo, so the repo's own numbers are the whole table.

## Roadmap summary

Done: the full hide and extract round trip, the capacity and length
checks, exit codes that tell the truth, and the shared bit loops the
two directions now use. Working now: nothing in flight. Next, if I
return to it: a real test file for the round trip, so the hand check
in the README stops being the only record. The full roadmap, with
the Later and Not planned sections, is in [ROADMAP.md](ROADMAP.md).
