from fluids.Fluid import *

def test_air_properties():
    air = Air()
    assert air.type == "Air"
    assert air.rho == 1.2
    assert air.viscosity == 0.000018

def test_water_properties():
    water = Water()
    assert water.type == "Water"
    assert water.rho == 1000
    assert water.viscosity == 1e-3

def test_custom_fluid():
    f = CustomFluid("Test", 50, 0.01)
    assert f.name == "Test"
    assert f.rho == 50
    assert f.viscosity == 0.01
