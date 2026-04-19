# stackfile

A CLI tool to snapshot and restore your local dev environment dependencies across machines.

---

## Installation

```bash
pip install stackfile
```

Or install from source:

```bash
git clone https://github.com/yourname/stackfile.git && cd stackfile && pip install .
```

---

## Usage

**Snapshot your current environment:**

```bash
stackfile snapshot
```

This generates a `stackfile.lock` capturing your current dependencies (pip packages, Node modules, system tools, etc.).

**Restore an environment from a snapshot:**

```bash
stackfile restore
```

**Specify a custom snapshot file:**

```bash
stackfile snapshot --output my-env.lock
stackfile restore --file my-env.lock
```

**View what's in a snapshot:**

```bash
stackfile show
```

---

## Example Workflow

```bash
# On your work machine
stackfile snapshot

# Commit stackfile.lock to your repo, then on a new machine:
git pull
stackfile restore
```

---

## License

MIT © 2024 [Your Name](https://github.com/yourname)