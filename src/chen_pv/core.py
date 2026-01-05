"""
Cálculo do loop Pressão–Volume baseado no template "Loop PV - metodo de chen.xlsm" (aba Planilha2).

O objetivo aqui NÃO é "adivinhar" a fisiologia; é replicar as fórmulas do template.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


Number = float


def _is_missing(x: Optional[Number]) -> bool:
    return x is None


def _safe_div(num: Optional[Number], den: Optional[Number]) -> Optional[Number]:
    if _is_missing(num) or _is_missing(den):
        return None
    if den == 0:
        return None
    return float(num) / float(den)


def _poly_endavg(tnd: Number) -> Number:
    # End(avg) = Σ ai * tNd^i, i=0..7, conforme coeficientes do template
    a0 = 0.35695
    a1 = -7.2266
    a2 = 74.249
    a3 = -307.39
    a4 = 684.54
    a5 = -856.92
    a6 = 571.95
    a7 = -159.1
    return (
        a0
        + a1 * tnd
        + a2 * (tnd ** 2)
        + a3 * (tnd ** 3)
        + a4 * (tnd ** 4)
        + a5 * (tnd ** 5)
        + a6 * (tnd ** 6)
        + a7 * (tnd ** 7)
    )


@dataclass(frozen=True)
class PVLoopPoints:
    """
    Pontos (volume, pressão) em mmHg/mL para plotar:
    - ESPVR: reta (V0,0) -> (VSF,Ptop)
    - Loop PV: polígono fechado
    """
    espvr: Tuple[Tuple[Number, Number], Tuple[Number, Number]]
    loop: Tuple[Tuple[Number, Number], ...]


def compute_metrics(
    *,
    PAS: Optional[Number] = None,
    PAD: Optional[Number] = None,
    VDF: Optional[Number] = None,
    VSF: Optional[Number] = None,
    PET: Optional[Number] = None,
    ET: Optional[Number] = None,
    Ees: Optional[Number] = None,
    V0: Optional[Number] = None,
) -> Dict[str, Optional[Number]]:
    """
    Replica as fórmulas da planilha (Planilha2, coluna B).

    Convenção:
    - Entrada ausente => resultado None (imitando IF(...,"",...) do Excel).
    - Divisão por zero => None.

    Retorna dict com chaves:
    PAt, VS, FE, tNd, Endavg, Endest, Ea, VAC, Ptop
    """
    out: Dict[str, Optional[Number]] = {}

    # PAt = 0.9 * PAS
    out["PAt"] = None if _is_missing(PAS) else 0.9 * float(PAS)

    # VS = VDF - VSF
    if _is_missing(VDF) or _is_missing(VSF):
        out["VS"] = None
    else:
        out["VS"] = float(VDF) - float(VSF)

    # FE (%) = (VDF - VSF)/VDF * 100
    if _is_missing(VDF) or _is_missing(VSF) or VDF == 0:
        out["FE"] = None
    else:
        out["FE"] = (float(VDF) - float(VSF)) / float(VDF) * 100.0

    # tNd = PET/ET
    out["tNd"] = _safe_div(PET, ET)

    # Endavg = poly(tNd)
    if _is_missing(out["tNd"]):
        out["Endavg"] = None
    else:
        out["Endavg"] = _poly_endavg(float(out["tNd"]))  # type: ignore[arg-type]

    # Endest = 0.0275 -0.165*(FE/100) +0.3656*(PAD/PAt) +0.515*Endavg
    if _is_missing(out["Endavg"]) or _is_missing(out["FE"]) or _is_missing(PAD) or _is_missing(out["PAt"]):
        out["Endest"] = None
    else:
        pat = out["PAt"]
        if pat in (None, 0):
            out["Endest"] = None
        else:
            out["Endest"] = (
                0.0275
                - 0.165 * (float(out["FE"]) / 100.0)  # type: ignore[arg-type]
                + 0.3656 * (float(PAD) / float(pat))
                + 0.515 * float(out["Endavg"])  # type: ignore[arg-type]
            )

    # Ea = PAt / VS
    out["Ea"] = _safe_div(out["PAt"], out["VS"])

    # VAC = Ea / Ees
    out["VAC"] = _safe_div(out["Ea"], Ees)

    # Ptop = Ees * (VSF - V0)
    if _is_missing(Ees) or _is_missing(VSF) or _is_missing(V0):
        out["Ptop"] = None
    else:
        out["Ptop"] = float(Ees) * (float(VSF) - float(V0))

    # Ees_chen (estimativa single-beat, conforme Chen et al.)
    # Fórmula (forma usual): Ees = [PAD - (ENd_est * 0.9*PAS)] / (ENd_est * VS)
    endest = out.get("Endest")
    vs = out.get("VS")
    if _is_missing(PAS) or _is_missing(PAD) or _is_missing(endest) or _is_missing(vs) or endest == 0 or vs == 0:
        out["Ees_chen"] = None
    else:
        esp = 0.9 * float(PAS)
        out["Ees_chen"] = (float(PAD) - (float(endest) * esp)) / (float(endest) * float(vs))

    # VAC_chen = Ea / Ees_chen
    out["VAC_chen"] = _safe_div(out.get("Ea"), out.get("Ees_chen"))

    # Ptop_chen = Ees_chen * (VSF - V0)
    if _is_missing(out.get("Ees_chen")) or _is_missing(VSF) or _is_missing(V0):
        out["Ptop_chen"] = None
    else:
        out["Ptop_chen"] = float(out["Ees_chen"]) * (float(VSF) - float(V0))

    return out


def compute_pv_points(
    *,
    VDF: Optional[Number],
    VSF: Optional[Number],
    V0: Optional[Number],
    Ptop: Optional[Number],
) -> Optional[PVLoopPoints]:
    """
    Gera os pontos de plotagem, seguindo a lógica do template.

    Retorna None se faltar algum parâmetro.
    """
    if _is_missing(VDF) or _is_missing(VSF) or _is_missing(V0) or _is_missing(Ptop):
        return None

    vdf = float(VDF)
    vsf = float(VSF)
    v0 = float(V0)
    ptop = float(Ptop)

    espvr = ((v0, 0.0), (vsf, ptop))
    loop = (
        (vdf, 0.0),
        (vdf, ptop),
        (vsf, ptop),
        (vsf, 0.0),
        (vdf, 0.0),
    )
    return PVLoopPoints(espvr=espvr, loop=loop)
