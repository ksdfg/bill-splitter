#!/usr/bin/env bash

# cd ./app || exit
uv run uvicorn app.main:app --host=0.0.0.0 --port=80 --workers=$(( $(nproc) * 2 + 1 ))
