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


def test_elastic_isotropic():
    opy.wipe()
    opy.model('basic', '-ndm', 2, '-ndf', 3)
    v_is_int = 1
    v_is_float = 1.
    # with pytest.raises(opy.error):  # TODO: can't find error class
    #     opy.nDMaterial('ElasticIsotropic', 1, 1., v_is_int, 0.0)
    opy.nDMaterial('ElasticIsotropic', 1, 1., v_is_float, 0.0)

if __name__ == '__main__':
    test_elastic_isotropic()