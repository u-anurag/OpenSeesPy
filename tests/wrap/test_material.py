import openseespy.opensees as opy
import openseespy.wrap as opw


def test_UniaxialSteel01():
    osi = opw.OpenseesInstance(dimensions=2)

    # Define material
    bilinear_mat = opw.uniaxial_materials.UniaxialSteel01(osi, fy=1, e0=1, b=1)
