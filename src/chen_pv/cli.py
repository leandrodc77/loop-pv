from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, Optional

import pandas as pd

from .core import compute_metrics, compute_pv_points
from .excel_template import extract_schema, extract_values, fill_template
from .plotting import plot_pv_loop


INPUT_COLS = ["PAS", "PAD", "VDF", "VSF", "PET", "ET", "Ees", "V0"]


def _to_float_or_none(x: Any) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, float) and pd.isna(x):
        return None
    if isinstance(x, str) and x.strip() == "":
        return None
    try:
        return float(x)
    except Exception:
        return None


def cmd_compute(args: argparse.Namespace) -> int:
    df = pd.read_csv(args.input)
    missing = [c for c in INPUT_COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"CSV sem colunas obrigatórias: {missing}. Encontradas: {list(df.columns)}")

    out_rows = []
    for idx, row in df.iterrows():
        inputs = {c: _to_float_or_none(row[c]) for c in INPUT_COLS}
        metrics = compute_metrics(**inputs)  # type: ignore[arg-type]

        out = dict(row)
        out.update(metrics)

        # pontos (opcional)
        pts = compute_pv_points(VDF=inputs["VDF"], VSF=inputs["VSF"], V0=inputs["V0"], Ptop=metrics.get("Ptop"))
        if pts:
            out["ESPVR_V0"] = pts.espvr[0][0]
            out["ESPVR_P0"] = pts.espvr[0][1]
            out["ESPVR_VES"] = pts.espvr[1][0]
            out["ESPVR_PES"] = pts.espvr[1][1]
        out_rows.append(out)

    out_df = pd.DataFrame(out_rows)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    out_df.to_csv(args.output, index=False)
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    if args.schema:
        schema = extract_schema(args.workbook)
        payload = [s.__dict__ for s in schema]
    else:
        payload = extract_values(args.workbook)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return 0


def cmd_fill_template(args: argparse.Namespace) -> int:
    row = json.loads(args.row_json)
    if not isinstance(row, dict):
        raise SystemExit("--row-json precisa ser um objeto JSON, ex.: '{"PAS":120,...}'")

    # valida/filtra
    inputs: Dict[str, float] = {}
    for k in INPUT_COLS:
        if k in row and row[k] is not None:
            inputs[k] = float(row[k])

    if not inputs:
        raise SystemExit("Nenhuma entrada válida encontrada em --row-json.")

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    fill_template(template_path=args.template, output_path=args.output, inputs=inputs)
    return 0


def cmd_plot(args: argparse.Namespace) -> int:
    df = pd.read_csv(args.input)
    missing = [c for c in INPUT_COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"CSV sem colunas obrigatórias: {missing}. Encontradas: {list(df.columns)}")

    os.makedirs(args.outdir, exist_ok=True)

    id_col = args.id_col if args.id_col in df.columns else None

    for idx, row in df.iterrows():
        inputs = {c: _to_float_or_none(row[c]) for c in INPUT_COLS}
        metrics = compute_metrics(**inputs)  # type: ignore[arg-type]
        pts = compute_pv_points(VDF=inputs["VDF"], VSF=inputs["VSF"], V0=inputs["V0"], Ptop=metrics.get("Ptop"))
        if not pts:
            continue

        tag = str(row[id_col]) if id_col else f"row_{idx+1}"
        title = f"Loop PV — {tag}"
        out_path = os.path.join(args.outdir, f"{tag}.png")
        plot_pv_loop(pts, title=title, output_path=out_path)

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="chen-pv", description="Loop PV (método de Chen): extrair/calc/plot a partir do template .xlsm")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_compute = sub.add_parser("compute", help="Calcula métricas a partir de um CSV (batch).")
    p_compute.add_argument("--input", required=True, help="CSV com colunas PAS,PAD,VDF,VSF,PET,ET,Ees,V0 (e outras).")
    p_compute.add_argument("--output", required=True, help="CSV de saída.")
    p_compute.set_defaults(func=cmd_compute)

    p_extract = sub.add_parser("extract", help="Extrai valores (cache) ou schema do template .xlsm.")
    p_extract.add_argument("--workbook", required=True, help="Caminho do .xlsm.")
    p_extract.add_argument("--output", required=True, help="Arquivo .json de saída.")
    p_extract.add_argument("--schema", action="store_true", help="Exporta schema (labels, unidades e fórmulas) em vez de valores.")
    p_extract.set_defaults(func=cmd_extract)

    p_fill = sub.add_parser("fill-template", help="Preenche o template .xlsm com entradas e salva uma cópia.")
    p_fill.add_argument("--template", required=True, help="Template .xlsm.")
    p_fill.add_argument("--row-json", required=True, help="Objeto JSON com entradas, ex.: '{"PAS":120,...}'")
    p_fill.add_argument("--output", required=True, help="Arquivo .xlsm de saída.")
    p_fill.set_defaults(func=cmd_fill_template)

    p_plot = sub.add_parser("plot", help="Gera PNG do loop PV para cada linha do CSV.")
    p_plot.add_argument("--input", required=True, help="CSV com entradas.")
    p_plot.add_argument("--outdir", required=True, help="Diretório de saída dos PNGs.")
    p_plot.add_argument("--id-col", default="id", help="Nome da coluna para nomear arquivos (default: id).")
    p_plot.set_defaults(func=cmd_plot)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
