from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi.openapi.utils import get_openapi

from app.main import app


def main() -> None:
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description="AI Fitness & Task Tracker API",
    )
    out_dir = Path(__file__).resolve().parents[1] / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "openapi.json"
    out_file.write_text(json.dumps(schema, indent=2))
    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()







