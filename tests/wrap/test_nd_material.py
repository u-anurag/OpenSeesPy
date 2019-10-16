import openseespy.opensees as opy
import openseespy.wrap as opw
import pytest


def test_can_set_PressureIndependMultiYield():
    osi = opw.OpenseesInstance(dimensions=2)

    # Define material
    nd = 2
    rho = 1400
    ref_shear_modul = 40e6
    ref_bulk_modul = 60e6
    cohesi = 60e3
    peak_shear_stra = 0.02
    opw.nd_material.PressureIndependMultiYield(osi, nd, rho, ref_shear_modul, ref_bulk_modul,
                                               cohesi, peak_shear_stra)


def test_can_set_PM4Sand():
    osi = opw.OpenseesInstance(dimensions=2)

    # Define material
    d_r = 0.5
    hpo = 0.4
    g0 = 555.
    p_atm = 101.3
    rho = 1.7
    opw.nd_material.PM4Sand(osi, d_r, g0, hpo, rho, p_atm)
