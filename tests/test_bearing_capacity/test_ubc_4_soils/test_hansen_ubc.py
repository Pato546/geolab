import pytest

from geolysis.core.bearing_capacity.ubc_4_soils import SoilProperties
from geolysis.core.bearing_capacity.ubc_4_soils.hansen_ubc import (
    HansenBearingCapacityFactor,
    HansenUltimateBearingCapacity,
)
from geolysis.core.foundation import Shape, create_foundation

ERROR_TOL = 0.01


class TestHansenBCF:
    @classmethod
    def setup_class(cls):
        cls.h_bcf = HansenBearingCapacityFactor()

    @pytest.mark.parametrize(
        ("f_angle, r_value"), ((0, 5.14), (10, 8.34), (20, 14.83), (35, 46.13))
    )
    def test_n_c(self, f_angle, r_value):
        assert self.h_bcf.n_c(f_angle) == pytest.approx(r_value, ERROR_TOL)

    @pytest.mark.parametrize(
        ("f_angle, r_value"), ((0, 1.00), (10, 2.47), (20, 6.4), (35, 33.29))
    )
    def test_n_q(self, f_angle, r_value):
        assert self.h_bcf.n_q(f_angle) == pytest.approx(r_value, ERROR_TOL)

    @pytest.mark.parametrize(
        ("f_angle, r_value"), ((0, 0.00), (10, 0.47), (20, 3.54), (35, 40.69))
    )
    def test_n_gamma(self, f_angle, r_value):
        assert self.h_bcf.n_gamma(f_angle) == pytest.approx(r_value, ERROR_TOL)


class TestHansenUBC:
    def test_bearing_capacity(self):
        fs = create_foundation(
            depth=1.5,
            width=2.0,
            footing_shape=Shape.SQUARE,
        )
        soil_prop: SoilProperties = {
            "friction_angle": 20.0,
            "cohesion": 20.0,
            "moist_unit_wgt": 18.0,
        }
        t = HansenUltimateBearingCapacity(
            soil_properties=soil_prop, foundation_size=fs
        )
        assert t.bearing_capacity() == pytest.approx(809.36, ERROR_TOL)