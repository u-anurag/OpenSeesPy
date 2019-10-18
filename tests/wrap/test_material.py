import openseespy.opensees as opy
import openseespy.wrap as opw


def test_UniaxialSteel01():
    osi = opw.OpenseesInstance(dimensions=2)

    # Define material
    bilinear_mat = opw.uniaxial_material.Steel01(osi, fy=1, e0=1, b=1)


def test_bond_sp01():
    osi = opw.OpenseesInstance(dimensions=2)
    opw.uniaxial_material.BondSP01(osi, fy=1, sy=1.0, fu=1.0, su=1.0, b=1.0, big_r=1.0)


def test_bilinear_oil_damper():
    osi = opw.OpenseesInstance(dimensions=2)
    opw.uniaxial_material.BilinearOilDamper(osi, k=1.0, cd=1.0, fr=1.0, p=1.0, l_gap=0.0, nm=1, rel_tol=1e-6,
                                            abs_tol=1e-10, max_half=15)