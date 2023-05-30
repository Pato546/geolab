"""Terzaghi Bearing Capacity Analysis."""

import functools

import numpy as np

from geolab import DECIMAL_PLACES, deg2rad
from geolab.bearing_capacity import BCF
from geolab.utils import cos, exp, product, tan


class TerzaghiBCF(BCF):
    """Terzaghi Bearing Capacity Factors."""

    @deg2rad
    def __init__(self, ngamma_type="Meyerhof", *, friction_angle):
        self.phi = friction_angle
        self.ngamma_type = ngamma_type.casefold()

    @staticmethod
    @functools.cache
    def _nq(phi):
        num = exp(((3 * np.pi) / 2 - phi) * tan(phi))
        den = 2 * (cos(np.deg2rad(45) + (phi / 2)) ** 2)
        return num / den

    def nq(self):
        return round(self._nq(self.phi), DECIMAL_PLACES)

    def nc(self):
        if np.isclose(self.phi, 0.0):
            return 5.70

        _nc = (1 / tan(self.phi)) * (self._nq(self.phi) - 1)

        return round(_nc, DECIMAL_PLACES)

    def ngamma(self):
        if self.ngamma_type == "meyerhof":
            _ngamma = (self._nq(self.phi) - 1) * tan(1.4 * self.phi)
        elif self.ngamma_type == "hansen":
            _ngamma = 1.8 * (self._nq(self.phi) - 1) * tan(self.phi)
        else:
            raise TypeError("Available types are Meyerhof or Hansen")

        return round(_ngamma, DECIMAL_PLACES)


class TBC:
    """Terzaghi Bearing Capacity."""

    def __init__(
        self,
        cohesion: float,
        friction_angle: float,
        unit_weight_of_soil: float,
        foundation_depth: float,
        foundation_width: float,
        ngamma_type: str = "Meyerhof",
    ) -> None:
        """
        :param cohesion: cohesion of foundation soil :math:`(kN/m^2)`
        :type cohesion: float
        :param friction_angle: internal angle of friction (degrees)
        :type friction_angle: float
        :param unit_weight_of_soil: unit weight of soil :math:`(kN/m^3)`
        :type unit_weight_of_soil: float
        :param foundation_depth: depth of foundation :math:`d_f` (m)
        :type foundation_depth: float
        :param foundation_width: width of foundation (**b**) (m)
        :type foundation_width: float
        :param ngamma_type: specifies the type of ngamma formula to use. Available
                            values are ``Meyerhof`` and ``Hansen``
        :type ngamma_type: str
        """
        self.cohesion = cohesion
        self.gamma = unit_weight_of_soil
        self.fd = foundation_depth
        self.fw = foundation_width
        self._bearing_cap_factors = TerzaghiBCF(
            ngamma_type, friction_angle=friction_angle
        )

    @property
    def nq(self) -> float:
        r"""Terzaghi Bearing Capacity factor :math:`N_q`.

        .. math::

            N_q=\dfrac{e^{(\frac{3\pi}{2}-\phi)\tan\phi}}{2\cos^2\left(45^{\circ}+\frac{\phi}{2}\right)}

        :return: The bearing capacity factor :math:`N_q`
        :rtype: float
        """
        return self._bearing_cap_factors.nq()

    @property
    def nc(self) -> float:
        r"""Terzaghi Bearing Capacity factor :math:`N_c`.

        .. math::

            N_c = \cot \phi \left(N_q - 1 \right)

        :return: The bearing capacity factor :math:`N_c`
        :rtype: float
        """
        return self._bearing_cap_factors.nc()

    @property
    def ngamma(self) -> float:
        r"""Terzaghi Bearing Capacity factor :math:`N_\gamma`.

        .. note::

            Exact values of :math:`N_\gamma` are not directly obtainable; values have
            been proposed by ``Brinch Hansen (1968)`` which are widely used in Europe,
            and also by ``Meyerhof (1963)``, which have been adopted in North America.

        The formulas shown below are ``Brinch Hansen`` and ``Meyerhof`` respectively.

        .. math::

            N_\gamma = 1.8 \left(N_q - 1 \right) \tan \phi

            N_\gamma = \left(N_q -1 \right)\tan(1.4\phi)

        :return: The bearing capacity factor :math:`N_\gamma`
        :rtype: float
        """
        return self._bearing_cap_factors.ngamma()

    def qult_4_strip_footing(self) -> float:
        r"""Ultimate bearing capacity according to ``Terzaghi`` for ``strip footing``.

        .. math::

            q_u = cN_c + \gamma D_f N_q + 0.5 \gamma B N_\gamma

        :return: ultimate bearing capacity of the soil :math:`(q_{ult})`
        :rtype: float
        """
        qult = (
            product(self.cohesion, self.nc)
            + product(self.gamma, self.fd, self.nq)
            + product(0.5, self.gamma, self.fw, self.ngamma)
        )

        return round(qult, DECIMAL_PLACES)

    def qult_4_square_footing(self):
        r"""Ultimate bearing capacity according to ``Terzaghi`` for ``square footing``.

        .. math::

            q_u = 1.2cN_c + \gamma D_f N_q + 0.4 \gamma B N_\gamma

        :return: ultimate bearing capacity of the soil :math:`(q_{ult})`
        :rtype: float
        """
        qult = (
            product(1.2, self.cohesion, self.nc)
            + product(self.gamma, self.fd, self.nq)
            + product(0.4, self.gamma, self.fw, self.ngamma)
        )

        return round(qult, DECIMAL_PLACES)

    def qult_4_circular_footing(self):
        r"""Ultimate bearing capacity according to ``Terzaghi`` for ``circular footing``.

        .. math::

            q_u = 1.2cN_c + \gamma D_f N_q + 0.3 \gamma B N_{\gamma}

        :return: ultimate bearing capacity of the soil :math:`(q_{ult})`
        :rtype: float
        """
        qult = (
            product(1.2, self.cohesion, self.nc)
            + product(self.gamma, self.fd, self.nq)
            + product(0.3, self.gamma, self.fw, self.ngamma)
        )

        return round(qult, DECIMAL_PLACES)
