import pytest

from analisis_estabilidad.elementos.estribo.estabilidad_global import (
    FALSE_FOOTING,
    GEOM,
    LOADS,
    MAT,
    SEISMIC,
    FalseFootingProperties,
    SubstructureAnalysis,
)


CASE_KEYS = (
    "case_service_I",
    "case_resistance_Ia",
    "case_resistance_Ib",
    "case_extreme_event_I",
)


def _analysis(false_footing=FALSE_FOOTING):
    return SubstructureAnalysis(
        GEOM, MAT, LOADS, SEISMIC, false_footing
    ).run_full_analysis()


@pytest.mark.parametrize("case_key", CASE_KEYS)
def test_interfaz_2_equilibrio_y_presion_referidos_a_su_base(case_key):
    case = _analysis()["interfaces"]["interface_2"]["cases"][case_key]

    fv = sum(item["valor"] for item in case["fv_detail"])
    me = sum(item["momento"] for item in case["fv_detail"])
    fh = sum(item["valor"] for item in case["fh_detail"])
    mv = sum(item["momento"] for item in case["fh_detail"])
    xo = (me - mv) / fv
    e = abs(case["support_width"] / 2.0 - xo)
    effective_width = case["support_width"] - 2.0 * case["overturning"]["e"]
    q_meyerhof = fv / effective_width / 10.0

    assert case["Fv"] == pytest.approx(fv, abs=0.02)
    assert case["Me"] == pytest.approx(me, abs=0.02)
    assert case["Fh"] == pytest.approx(fh, abs=0.02)
    assert case["Mv"] == pytest.approx(mv, abs=0.02)
    assert case["overturning"]["Xo"] == pytest.approx(xo, abs=0.01)
    assert case["overturning"]["e"] == pytest.approx(e, abs=0.006)
    assert case["bearing"]["effective_width"] == pytest.approx(
        effective_width, abs=0.001
    )
    assert case["bearing"]["q"] == pytest.approx(q_meyerhof, abs=0.001)


def test_interfaz_2_traslada_brazos_a_la_punta_de_la_falsa_zapata():
    offset = 1.20
    false_footing = FalseFootingProperties(
        width=14.00,
        height=3.74,
        offset_from_toe=offset,
    )
    results = _analysis(false_footing)
    upper = results["interfaces"]["interface_1"]["cases"]["case_service_I"]
    lower = results["interfaces"]["interface_2"]["cases"]["case_service_I"]

    upper_vertical = {
        (item["origen"], item["desc"]): item for item in upper["fv_detail"]
    }
    for item in lower["fv_detail"]:
        if item["desc"] == "Falsa zapata":
            assert item["brazo"] == pytest.approx(false_footing.width / 2.0)
            assert item["momento"] == pytest.approx(
                item["valor"] * item["brazo"], abs=0.02
            )
            continue
        upper_item = upper_vertical[(item["origen"], item["desc"])]
        assert item["brazo"] == pytest.approx(upper_item["brazo"] + offset)

    lower_horizontal = {item["tipo"]: item for item in lower["fh_detail"]}
    assert lower_horizontal["Ea"]["brazo"] == pytest.approx(
        (GEOM.H + false_footing.height) / 3.0, abs=0.01
    )
    assert lower_horizontal["Es"]["brazo"] == pytest.approx(
        (GEOM.H + false_footing.height) / 2.0, abs=0.01
    )
    upper_br = next(item for item in upper["fh_detail"] if item["tipo"] == "BR")
    assert lower_horizontal["BR"]["brazo"] == pytest.approx(
        upper_br["brazo"] + false_footing.height
    )
