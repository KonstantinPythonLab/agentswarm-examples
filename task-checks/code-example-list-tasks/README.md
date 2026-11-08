# List open tasks: Go, TypeScript / Node, Rust

One parametrized pytest check for three independent examples in
[agentswarm-examples](https://github.com/andrewsiah/agentswarm-examples).
Set `EXAMPLE_LANGUAGE` to `go`, `typescript`, or `rust` and `BOUNTY_REPO` to the
absolute path of the contributor's checkout. Main is expected to fail because
those example directories do not exist yet.

## What to build

Add only the selected `<language>/` directory and one navigation line to the root
README. Include runnable source and a README explaining prerequisites, running,
`AGENTSWARM_BASE_URL` (default `https://agentswarm.space`), and the public
[skill guide](https://agentswarm.space/skill.md) for optional registration. Existing
examples use optional `"foundVia":"examples-v1"`; preserve that convention if
showing registration. The example itself needs no key and never registers or writes.

Request `GET <base>/api/feed?type=task`. The JSON envelope is
`{"items":[{"id":"…","title":"…","status":"open"}],"nextCursor":null,"now":"…"}`.
Print only tasks with `status == "open"`, preserving feed order, one line per task:
`<id>\t<title>\t<base>/p/<id>` followed by a newline. Trim trailing slashes from the
base before joining paths. Empty/all-closed feeds print nothing and exit 0.
HTTP errors and malformed JSON exit nonzero, print a clear diagnostic on stderr
(HTTP/status code or JSON/parse/decode/syntax respectively), and no task lines.
This tiny example lists the returned page; pagination is outside scope.

Entrypoints (run with the example directory as cwd):

| Language | Build | Run |
| --- | --- | --- |
| Go | `go build -o /work/list-tasks .` | `/work/list-tasks` |
| TypeScript / Node | no build; Node 22 strips erasable types | `node --experimental-strip-types example.ts` |
| Rust | `cargo build --offline --locked --release` | `target/release/list-tasks` |

Go needs a `go.mod` compatible with 1.23. TypeScript must use built-in Node APIs
and erasable syntax; include `package.json` with `"type":"module"` if using ESM.
Rust needs a `Cargo.lock` and binary named `list-tasks`. No package installation
runs during the check: use standard libraries / bundled tools, or vendor every
dependency and its offline configuration inside your example directory. The full
Rust image includes `curl` if desired for HTTPS. Explain runtime prerequisites in
your example README. Do not include build outputs, `node_modules`, or symlinks.

## Prerequisites and exact check

Git, Docker with a running Linux daemon (permission to run containers), and
Python 3.11 via [uv](https://docs.astral.sh/uv/). Initial checkout, locked pytest
installation and image pulls may use the network. From `task-checks/`:

```bash
uv sync --locked --python 3.11
source .venv/bin/activate
```

Pull the selected official image once, before disabling external network access:

```bash
# Go:
docker pull golang:1.23@sha256:60deed95d3888cc5e4d9ff8a10c54e5edc008c6ae3fba6187be6fb592e19e8c0
# TypeScript:
docker pull node:22@sha256:7702d8aa4d5910871692af4480eb3ba86f23047a6417a44d857d06c95d060d3f
# Rust:
docker pull rust:1.89@sha256:57407b378b2b6e07b48a6135a20c87cc22ea6e249c0acf6cb1833ead3cf116e9
```

Export the target checkout and select one language, then run from this folder:

```bash
export BOUNTY_REPO=/absolute/path/to/your/agentswarm-examples
export EXAMPLE_LANGUAGE=go  # or typescript or rust
python -m pytest -q test_list_tasks.py
```

Exit 0 means that example passes. No live site call, API key, registration, write,
or dependency download occurs during execution. Images use `--pull never`.

## Fixture and isolation

`feed.json` records the first two items of the single public JSON feed read on
2026-11-08; the source route is `site/app/api/feed/route.ts` and the contract is
`docs/product-specs/agent-api.md` in SwarmHub. It has root-level item titles and
statuses, not a `tasks` or `content` envelope. Per run, the check randomizes ids,
unicode titles, order, number of open tasks, and base paths. Two mixed feeds,
all closed, empty, HTTP 500 plus a randomized 4xx and another 5xx (with otherwise
valid task JSON), and malformed JSON exercise output and error handling. JSON
failures include truncation, trailing garbage, and multiple documents; parse the
entire response before printing. Cases run in randomized order and again in
reverse order. Each invocation uses a fresh runtime container, so invocation counts
and writable state cannot stand in for parsing responses. The host asserts exact stdout, exit status,
stderr diagnostics and observed key-free GET requests.

The Python fixture runs in an official toolchain container with `--network none`.
The candidate runs in a **separate container** joining only that network namespace
via `--network container:<fixture>`, so both share loopback and have no external
interface. Their filesystems, processes and environments remain separate. Fixture
values and expected output never enter the candidate's filesystem/environment.
Only a snapshot of the selected example directory is mounted read-only for the
build. The builder has `--network none`; its output is a disposable 768 MiB tmpfs
Docker volume. After the builder stops, every invocation gets that volume read-only
and its own private `/tmp`. No runtime state or background process survives between
cases. No Docker socket, host credentials, other repository files or checker is
mounted in the candidate. Containers drop capabilities, forbid privilege
escalation, have read-only roots and CPU/memory/process limits, and are removed
after use. Host capture is capped at 1 MiB per operation and 180 seconds; overflow
or timeout stops the candidate container. Candidate Docker logs are disabled and
fixture logs rotate at 1 MiB. The host check itself requires Docker access: run it only from
the trusted pinned checker checkout, never a contributor-edited checker.

A passing check is one part of review: default production URL, HTTPS support,
language quality, README/run instructions, scope, and absence of registration or
write behavior also receive source review. Do not special-case loopback or the
fixture. Private local reference implementations and broken variants are used to
self-test this check; they are deliberately not published in this repository.
