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
    opw.nd_materials.PressureIndependMultiYield(osi, nd, rho, ref_shear_modul, ref_bulk_modul,
                                                               cohesi, peak_shear_stra)
