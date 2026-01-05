#!/usr/bin/env python3
"""
Uso rápido:
  python scripts/dump_schema.py "Loop PV - metodo de chen.xlsm" > schema.json
"""
import json
import sys
from chen_pv.excel_template import extract_schema

path = sys.argv[1]
schema = extract_schema(path)
json.dump([s.__dict__ for s in schema], sys.stdout, ensure_ascii=False, indent=2)
sys.stdout.write("\n")
