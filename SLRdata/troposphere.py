import numpy as np


def wavelength_function(lam):
    """Wavelength-dependent function. lam is wavelength in nanometers."""
    lam = lam/1000
    return 0.9650 + 0.0164/lam**2 + 0.000228/lam**4

def site_function(phi, H):
    """Laser site function.
    
    phi is the latitude (in radians) and H is the geodetic height (in km)."""
    return 1 - 0.0026 * np.cos(2*phi) - 0.00031 * H

def term_A(P0, e0):
    """Term A in the main equation.
    
    P0 is the atmospheric pressure at the site (in hPa).
    e0 is the water vapor pressure at the site (in hPa)"""
    return 0.002357 * P0 + 0.000141 * e0

def term_B(T0, P0, K):
    """Term B in the main equation.
    
    T0 is the temperature (in Kelvin),
    P0 is the pressure (in hPa),
    K is the K term  (see below)."""
    return 1.084e-8 * P0*T0*K + 4.734e-8 * P0**2/T0 * 2/(3 - 1/K)

def term_K(T0, P0, phi):
    """Term K in the main equation.
    
    T0 is the temperature (in Kelvin),
    P0 is the pressure (in hPa),
    phi is the latitude of the station."""
    return 1.163 - 0.00968 * np.cos(2*phi) - 0.00104 * T0 + 0.00001435 * P0

def vapor_pressure(T, RH):
    """Vapor pressure at temperature T (Kelvin) relative humidity RH (%)."""
    exponent = 7.5*(T - 273.15) / (237.3 + (T - 273.15))
    return RH/100 * 6.11 * 10**exponent

def troposphere_correction(T, P, RH, latitude, height, elevation, lam=532):
    vapor = vapor_pressure(T, RH)
    A = term_A(P, vapor)
    K = term_K(T, P, latitude)
    B = term_B(T, P, K)
    f0 = wavelength_function(lam)
    f1 = site_function(latitude, height)
    se = np.sin(elevation)
    return f0/f1 * (A+B) / (se + (B/(A+B)) / (se + 0.01))


# =============================================================================
# Tests
#   Run these with 'python -m pytest troposphere.py'
#
# The tests compare the values returned to the functions to values computed
# by pen and paper from the equations. The comparison is mostly done at
# latitude 0°, standard temperature and pressure (273.15 K and 1013.25 hPa),
# relative humidity 50%, wavelength 532 nm, geodetic height 1000 meters,
# and satellite elevation 30°.
# The tests are done to six significant figures.

def test_wavelength_term():
    f0 = wavelength_function(694.3)
    np.testing.assert_approx_equal(f0, 1.0, 6)
    f0 = wavelength_function(532)
    np.testing.assert_approx_equal(f0, 1.02579196602, 6)
    f0 = wavelength_function(1064)
    np.testing.assert_approx_equal(f0, 0.979664, 6)


def test_site_term():
    f1 = site_function(0.0, 1.0)
    np.testing.assert_approx_equal(f1, 0.99709, 6)
    
def test_term_A():
    np.testing.assert_approx_equal(term_A(0,0), 0.0, 6)
    np.testing.assert_approx_equal(term_A(1,0), 0.002357, 6)
    np.testing.assert_approx_equal(term_A(0,1), 0.000141, 6)
    np.testing.assert_approx_equal(term_A(1,1), 0.002498, 6)
    e0 = vapor_pressure(273.15, 50)
    np.testing.assert_approx_equal(term_A(1013.25, e0), 2.388661005, 6)

def test_term_K():
    K = term_K(273.15, 1013.25, 0.0)
    np.testing.assert_approx_equal(K, 0.8837841375, 6)

def test_vapor():
    e0 = vapor_pressure(273.15, 50)
    np.testing.assert_approx_equal(e0, 3.055, 6)

def test_term_B():
    K = term_K(273.15, 1013.25, 0.0)
    B = term_B(273.15, 1013.25, K)
    np.testing.assert_approx_equal(B, 0.00284196709, 6)

def test_correction():
    T = 273.15
    P = 1013.25
    RH = 50.0
    height = 1.0
    elevation = 30.0 * np.pi/180
    latitude = 0.0
    lam = 532
    deltaR = troposphere_correction(T, P, RH, latitude, height, elevation, lam)
    np.testing.assert_approx_equal(deltaR, 4.897863, 6)
    
    