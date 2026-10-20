#!/bin/sh
# Read-only wrapper. Python 3.9+; root is optional and defaults to this package.
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
    python_cmd=python3
elif command -v python >/dev/null 2>&1; then
    python_cmd=python
else
    printf '%s\n' 'Python 3.9+ is required. No dependencies will be installed.' >&2
    exit 1
fi

if ! "$python_cmd" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
    printf '%s\n' 'The selected Python interpreter must be version 3.9 or later.' >&2
    exit 1
fi

exec "$python_cmd" "$script_dir/validate-skill.py" "$@"
