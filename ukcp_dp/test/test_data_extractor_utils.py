import iris
from cf_units import Unit

from ukcp_dp.data_extractor._utils import _make_anomaly


def test_make_anomaly_percentage_change():
    u = Unit('%')
    c = iris.cube.Cube([15.], long_name='rain', units='%')
    ref = iris.cube.Cube([10.], long_name='rain', units='%')
    anom = _make_anomaly(c, ref, u)
    assert(anom.data[0] == 50)


def test_make_anomaly_absolute_change():
    u = Unit('Celsius')
    c = iris.cube.Cube([15.], long_name='temp', units='degC')
    ref = iris.cube.Cube([10.], long_name='temp', units='degC')
    anom = _make_anomaly(c, ref, u)
    assert(anom.data[0] == 5)

