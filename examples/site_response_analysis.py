import eqsig
from eqsig import duhamels
from collections import OrderedDict
import numpy as np
import sfsimodels as sm
import openseespy.opensees as opy
import openseespy.wrap as opw


def site_response(sp, asig):
    """
    Run seismic analysis of a soil profile - example based on:
    http://opensees.berkeley.edu/wiki/index.php/Site_Response_Analysis_of_a_Layered_Soil_Column_(Total_Stress_Analysis)

    :param sp: sfsimodels.SoilProfile object
        A soil profile
    :param asig: eqsig.AccSignal object
        An acceleration signal
    :return:
    """

    osi = opw.OpenseesInstance(dimensions=2)
    assert isinstance(sp, sm.SoilProfile)
    dis_profile = sp.gen_split(props=['shear_vel', 'unit_mass', 'cohesion', 'bulk_modulus', 'poissons_ratio'])
    thicknesses = sp.split["thickness"]
    n_node_rows = len(thicknesses) + 1
    depths = np.cumsum(sp.split["thickness"])
    shear_vels = sp.split["shear_vel"]
    unit_masses = sp.split["unit_mass"] / 1e3
    g_mods = unit_masses * shear_vels ** 2
    poissons_ratio = sp.split['poissons_ratio']
    elastic_mods = 2 * g_mods * (1 - poissons_ratio)
    bulk_mods = elastic_mods / (3 * (1 - 2 * poissons_ratio))
    gamma_peak = 0.1
    ref_pressure = 80.0
    cohesions = sp.layer(1).cohesion  # TODO: add the discretizer

    damping = 0.02
    omega_1 = 2 * np.pi * 0.2
    omega_2 = 2 * np.pi * 20
    a0 = 2 * damping * omega_1 * omega_2 / (omega_1 + omega_2)
    a1 = 2 * damping / (omega_1 + omega_2)

    newmark_gamma = 0.5
    newmark_beta = 0.25

    ele_width = min(thicknesses)
    total_soil_nodes = len(thicknesses) * 2 + 2

    nd = OrderedDict()
    nd["R0L"] = opw.nodes.Node(osi, 0, 0)  # row 0 left
    nd["R0R"] = opw.nodes.Node(osi, ele_width, 0)
    for i in range(len(thicknesses)):
        # Establish nodes
        nd["R%iL" % (i + 1)] = opw.nodes.Node(osi, 0, -depths[i])
        nd["R%iR" % (i + 1)] = opw.nodes.Node(osi, ele_width, -depths[i])
        opw.EqualDOF(osi, nd["R%iL" % (i + 1)], nd["R%iR" % (i + 1)], [opw.static.X, opw.static.Y])

    # Fix base nodes
    opw.Fix(osi, nd["R%iL" % n_node_rows], opw.static.FIXED, opw.static.FIXED, opw.static.FREE)
    opw.Fix(osi, nd["R%iR" % n_node_rows], opw.static.FIXED, opw.static.FIXED, opw.static.FREE)

    # Define dashpots
    dashpot_node_l = opw.nodes.Node(osi, 0, depths[-1])
    dashpot_node_2 = opw.nodes.Node(osi, 0, depths[-1])
    opw.Fix(osi, dashpot_node_l,  opw.static.FIXED, opw.static.FIXED, opw.static.FREE)
    opw.Fix(osi, dashpot_node_2, opw.static.FREE, opw.static.FIXED, opw.static.FREE)

    # define equal DOF for dashpot and soil base nodes
    opw.EqualDOF(osi, nd["R%iL" % n_node_rows], nd["R%iR" % n_node_rows], [opw.static.X])
    opw.EqualDOF(osi, nd["R%iL" % n_node_rows], dashpot_node_l, [opw.static.X])



    return outputs


def run():
    sl = sm.Soil()
    vs = 250.
    unit_mass = 1700.0
    sl.g_mod = vs ** 2 * unit_mass
    sl.poissons_ratio = 0.0
    sl.unit_dry_weight = unit_mass * 9.8
    assert np.isclose(vs, sl.calc_shear_vel(saturated=False))
    sp = sm.SoilProfile()
    sp.add_layer(0, sl)
    sp.height = 30.0


if __name__ == '__main__':
    run()