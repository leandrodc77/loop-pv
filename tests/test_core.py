import pytest

from chen_pv.core import compute_metrics, compute_pv_points


def test_basic_outputs_match_template_example():
    metrics = compute_metrics(VDF=67.35, VSF=34.35, Ees=2.39, V0=-8.21)

    assert metrics["VS"] == pytest.approx(33.0)
    assert metrics["FE"] == pytest.approx(48.9977728285)
    assert metrics["Ptop"] == pytest.approx(101.7184)


def test_points_generation():
    metrics = compute_metrics(VDF=67.35, VSF=34.35, Ees=2.39, V0=-8.21)
    pts = compute_pv_points(VDF=67.35, VSF=34.35, V0=-8.21, Ptop=metrics["Ptop"])
    assert pts is not None
    assert pts.loop[0] == (pytest.approx(67.35), pytest.approx(0.0))
    assert pts.espvr[0] == (pytest.approx(-8.21), pytest.approx(0.0))
