"""Allow `python -m tools.domain_e2e.runner` from repo root."""

from tools.domain_e2e.runner import main

if __name__ == "__main__":
    raise SystemExit(main())
