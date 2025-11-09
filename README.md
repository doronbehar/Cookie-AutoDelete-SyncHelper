# Cookie-AutoDelete Container Migrator

Python tool to migrate [Cookie-AutoDelete](https://github.com/Cookie-AutoDelete/Cookie-AutoDelete) expression lists between Firefox profiles with different container IDs.

## The Problem

Cookie-AutoDelete (CAD) exports configuration using Firefox container IDs rather than container names.
When you create a new Firefox profile (e.g on a new computer), and install the [Multi-Account containers extension](https://addons.mozilla.org/firefox/addon/multi-account-containers/), Firefox recreates your containers with new IDs, breaking your CAD configuration.
This makes syncing CAD settings across machines difficult (see issues [#30](https://github.com/Cookie-AutoDelete/Cookie-AutoDelete/issues/30) & [#1718](https://github.com/Cookie-AutoDelete/Cookie-AutoDelete/issues/1718)).

## What This Tool Does

This script translates CAD expression lists from one Firefox profile's container IDs to another profile's container IDs by matching container names.

## Installation

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

Or if you want to do it manually, and you have [`questionary`](https://github.com/tmbo/questionary) installed for the default `python` executable in your `$PATH`:

```bash
ln -s src/CAD_sync/__init__.py ~/.bin/CAD-sync.py
```

## Usage

### With Original Containers File (Automated)

If you have the `containers.json` from your original machine:

```bash
cad-container-migrator \
  -i CAD_expressions-in.json \
  -O original-containers.json \
  -c current-containers.json \
  -o CAD_expressions-out.json
```

### Without Original Containers File (Interactive)

If you don't have the original `containers.json`, maybe because you have only a backup of `CAD_expressions-in.json`, the tool will interactively ask you to match each set of URL expressions to a container name, and this feature requires [`questionary`](https://github.com/tmbo/questionary):

```bash
cad-container-migrator \
  -i CAD_expressions-in.json \
  -c current-containers.json \
  -o CAD_expressions-out.json
```

## Migration Steps

### Machine A (Source)
1. Export CAD expressions: `CAD_expressions-in.json`
2. (Optional) Copy `containers.json` from your profile directory at `~/.mozilla/firefox/` as `original-containers.json`

### Machine B (Target)
3. Locate your profile in `~/.mozilla/firefox/` and in it find `containers.json`
4. Run the migration script using the path to the above
5. Import the output `CAD_expressions-out.json` into CAD

## Options

- `-i, --input-expressions` (required): Input CAD expressions JSON file
- `-O, --original-containers` (optional): Original containers.json for automatic matching
- `-c, --current-containers` (required): Current profile's containers.json
- `-o, --output-expressions` (required): Output file for migrated expressions

## Requirements

- Python 3.9+
- [`questionary`](https://github.com/tmbo/questionary) (for interactive mode only)

## Complementary Extensions

Besides [Multi-Account containers extension](https://addons.mozilla.org/firefox/addon/multi-account-containers/), I also recommend [Container Traffic Control](https://addons.mozilla.org/en-US/firefox/addon/ctc/) to control which URLs and domains are opened by which containers.
