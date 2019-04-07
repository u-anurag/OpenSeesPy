from collections import OrderedDict

import matplotlib.pyplot as plt
import sfsimodels
import eqsig

import numpy as np

from openseespy import opensees as opy  # private package
import openseespy.wrap.static as opc
import openseespy.wrap as opw


def calc_yield_curvature(depth, eps_yield):
    """
    The yield curvature of a section from Priestley (Fig 4.15)

    :param depth:
    :param eps_yield:
    :return:
    """
    # TODO: get full validation of equation
    return 2.1 * eps_yield / depth


def elastic_bilin(ep1, ep2, eps_p2, en1=None, en2=None, eps_n2=None):
    if en1 is None:
        en1 = ep1
    if en2 is None:
        en2 = ep2
    if eps_n2 is None:
        eps_n2 = eps_p2

    return [ep1, ep2, eps_p2, en1, en2, eps_n2]


def get_inelastic_response(fb, motion, dt, extra_time=0.0, xi=0.05, analysis_dt=0.001):
    """
    Run seismic analysis of a nonlinear FrameBuilding

    :param mass: SDOF mass
    :param k_spring: spring stiffness
    :param f_yield: yield strength
    :param motion: list, acceleration values
    :param dt: float, time step of acceleration values
    :param extra_time: float, additional analysis time after end of ground motion
    :param xi: damping ratio
    :param r_post: post-yield stiffness
    :return:
    """
    osi = opw.OpenseesInstance(dimensions=2)

    q_floor = 10000.  # kPa
    trib_width = fb.floor_length
    trib_mass_per_length = q_floor * trib_width / 9.8

    # Establish nodes and set mass based on trib area
    # Nodes named as: C<column-number>-S<storey-number>, first column starts at C1-S0 = ground level left
    nd = OrderedDict()
    col_xs = np.cumsum(fb.bay_lengths)
    col_xs = np.insert(col_xs, 0, 0)
    n_cols = len(col_xs)
    sto_ys = fb.heights
    sto_ys = np.insert(sto_ys, 0, 0)
    for cc in range(1, n_cols + 1):
        for ss in range(fb.n_storeys + 1):
            nd["C{0}-S{1}".format(cc, ss)] = opw.nodes.Node(osi, col_xs[cc - 1], sto_ys[ss])

            if ss != 0:
                if cc == 1:
                    node_mass = trib_mass_per_length * fb.bay_lengths[0] / 2
                elif cc == n_cols:
                    node_mass = trib_mass_per_length * fb.bay_lengths[-1] / 2
                else:
                    node_mass = trib_mass_per_length * (fb.bay_lengths[cc - 2] + fb.bay_lengths[cc - 1] / 2)
                opw.set_node_mass(nd["C{0}-S{1}".format(cc, ss)], node_mass, 0., 0.)

    # Set all nodes on a storey to have the same displacement
    for ss in range(0, fb.n_storeys + 1):
        for cc in range(1, n_cols + 1):
            opw.set_equal_dofs(nd["C{0}-S{1}".format(1, ss)], nd["C{0}-S{1}".format(cc, ss)], opc.X)

    # Fix all base nodes
    for cc in range(1, n_cols + 1):
        opy.fix(nd["C%i-S%i" % (cc, 0)].tag, opc.FIXED, opc.FIXED, opc.FIXED)

    # Coordinate transformation
    geo_tag = 1
    trans_args = []
    opy.geomTransf("Linear", geo_tag, *[])

    l_hinge = fb.bay_lengths[0] * 0.1

    # Define material
    e_conc = 30.0e6
    i_beams = 0.4 * fb.beam_widths * fb.beam_depths ** 3 / 12
    i_columns = 0.5 * fb.column_widths * fb.column_depths ** 3 / 12
    a_beams = fb.beam_widths * fb.beam_depths
    a_columns = fb.column_widths * fb.column_depths
    ei_beams = e_conc * i_beams
    ei_columns = e_conc * i_columns
    eps_yield = 300.0e6 / 200e9
    phi_y_col = calc_yield_curvature(fb.column_depths, eps_yield)
    phi_y_beam = calc_yield_curvature(fb.beam_depths, eps_yield) * 10  # TODO: re-evaluate

    # Define beams and columns

    md = OrderedDict()  # material dict
    sd = OrderedDict()  # section dict
    ed = OrderedDict()  # element dict
    # Columns named as: C<column-number>-S<storey-number>, first column starts at C1-S0 = ground floor left
    # Beams named as: B<bay-number>-S<storey-number>, first beam starts at B1-S1 = first storey left (foundation at S0)

    transf_tag = 2
    opy.geomTransf('Linear', transf_tag, *[])

    for ss in range(fb.n_storeys):

        # set columns
        for cc in range(1, fb.n_cols + 1):
            ele_tag = cc * 100 + ss
            print(ele_tag)
            md["C{0}-S{1}S{2}".format(cc, ss, ss + 1)] = ele_tag
            sd["C{0}-S{1}S{2}".format(cc, ss, ss + 1)] = ele_tag

            yy = phi_y_col[ss][cc - 1] * ei_columns[ss][cc - 1]
            mat_type = 'Steel01'
            lp_i = 0.4
            lp_j = 0.4  # plastic hinge length

            mat_args = [300e6, 200e9, 0.001]
            mat_tag = ele_tag
            left_sect_tag = ele_tag
            right_sect_tag = 1000 * ele_tag
            centre_sect_tag = 10000 * ele_tag
            opy.uniaxialMaterial(mat_type, mat_tag, *mat_args)

            # opy.section("Uniaxial", left_sect_tag, mat_tag, "Mz")
            # opy.section("Uniaxial", right_sect_tag, mat_tag, "Mz")
            # central section
            e_conc = 30e6
            area = 0.3 * 0.4
            inertia = 0.3 * 0.4 ** 3 / 12
            top_sect = opw.sections.Elastic(osi, e_conc, area, inertia)
            bot_sect = opw.sections.Elastic(osi, e_conc, area, inertia)
            centre_sect = opw.sections.Elastic(osi, e_conc, area, inertia)
            sd["C{0}-S{1}S{2}T".format(cc, ss, ss + 1)] = top_sect
            sd["C{0}-S{1}S{2}B".format(cc, ss, ss + 1)] = bot_sect
            sd["C{0}-S{1}S{2}C".format(cc, ss, ss + 1)] = centre_sect

            integ_tag = ele_tag
            opy.beamIntegration('HingeMidpoint', integ_tag, bot_sect.tag, lp_i, top_sect.tag, lp_j, centre_sect.tag)

            left_node = nd["C%i-S%i" % (cc, ss)].tag
            right_node = nd["C%i-S%i" % (cc, ss + 1)].tag
            opy.element('forceBeamColumn', ele_tag, left_node, right_node, transf_tag, integ_tag)

        # Set beams
        for bb in range(1, fb.n_bays + 1):
            ele_tag = bb * 10000 + ss
            mat_tag = ele_tag
            left_sect_tag = ele_tag
            right_sect_tag = 1000 * ele_tag
            centre_sect_tag = 10000 * ele_tag
            lp_i = 0.5
            lp_j = 0.5
            md["B%i-S%i" % (bb, ss)] = ele_tag
            sd["B%i-S%i" % (bb, ss)] = ele_tag
            ed["B%i-S%i" % (bb, ss)] = ele_tag
            mat_props = elastic_bilin(ei_beams[ss][bb - 1], 0.05 * ei_beams[ss][bb - 1], phi_y_beam[ss][bb - 1])
            opy.uniaxialMaterial('ElasticBilin', ele_tag, *mat_props)
            opy.section("Uniaxial", left_sect_tag, mat_tag, "Mz")
            opy.section("Uniaxial", right_sect_tag, mat_tag, "Mz")

            # central section
            e_conc = 30e6
            area = 0.3 * 0.4
            inertia = 0.3 * 0.4 ** 3 / 12

            # opy.section("Elastic", left_sect_tag, *[e_conc, area, inertia])
            # opy.section("Elastic", right_sect_tag, *[e_conc, area, inertia])
            opy.section("Elastic", centre_sect_tag, *[e_conc, area, inertia])

            integ_tag = ele_tag
            opy.beamIntegration('HingeMidpoint', integ_tag, left_sect_tag, lp_i, right_sect_tag, lp_j, centre_sect_tag)

            left_node = nd["C%i-S%i" % (bb, ss + 1)].tag
            right_node = nd["C%i-S%i" % (bb + 1, ss + 1)].tag
            opy.element('forceBeamColumn', ele_tag, left_node, right_node, transf_tag, integ_tag)

    # Define the dynamic analysis
    load_tag_dynamic = 1
    pattern_tag_dynamic = 1

    values = list(-1 * motion)  # should be negative
    opy.timeSeries('Path', load_tag_dynamic, '-dt', dt, '-values', *values)
    opy.pattern('UniformExcitation', pattern_tag_dynamic, opc.X, '-accel', load_tag_dynamic)

    # set damping based on first eigen mode
    angular_freq = opy.eigen('-fullGenLapack', 1) ** 0.5
    if isinstance(angular_freq, complex):
        raise ValueError("Angular frequency is complex, issue with stiffness or mass")
    alpha_m = 0.0
    beta_k = 2 * xi / angular_freq
    beta_k_comm = 0.0
    beta_k_init = 0.0

    opy.rayleigh(alpha_m, beta_k, beta_k_init, beta_k_comm)

    # Run the dynamic analysis

    opy.wipeAnalysis()

    opy.algorithm('Newton')
    opy.system('SparseGeneral')
    opy.numberer('RCM')
    opy.constraints('Transformation')
    opy.integrator('Newmark', 0.5, 0.25)
    opy.analysis('Transient')
    #op.test("NormDispIncr", 1.0e-1, 2, 0)
    tol = 1.0e-4
    iter = 4
    opy.test('EnergyIncr', tol, iter, 0, 2)
    analysis_time = (len(values) - 1) * dt + extra_time
    outputs = {
        "time": [],
        "rel_disp": [],
        "rel_accel": [],
        "rel_vel": [],
        "force": [],
        "ele_mom": [],
        "ele_curve": [],
    }
    print("Analysis starting")
    opy.recorder('Element', '-file', 'ele_out.txt', '-time', '-ele', 1, 'force')
    while opy.getTime() < analysis_time:
        curr_time = opy.getTime()
        opy.analyze(1, analysis_dt)
        outputs["time"].append(curr_time)
        outputs["rel_disp"].append(opy.nodeDisp(nd["C%i-S%i" % (1, fb.n_storeys)].tag, opc.X))
        outputs["rel_vel"].append(opy.nodeVel(nd["C%i-S%i" % (1, fb.n_storeys)].tag, opc.X))
        outputs["rel_accel"].append(opy.nodeAccel(nd["C%i-S%i" % (1, fb.n_storeys)].tag, opc.X))
        # outputs['ele_mom'].append(opy.eleResponse('-ele', [ed['B%i-S%i' % (1, 0)], 'basicForce']))
        opy.reactions()
        react = 0
        for cc in range(1, fb.n_cols):
            react += -opy.nodeReaction(nd["C%i-S%i" % (cc, 0)].tag, opc.X)
        outputs["force"].append(react)  # Should be negative since diff node
    opy.wipe()
    for item in outputs:
        outputs[item] = np.array(outputs[item])

    return outputs


# def load_frame_building_sample_data():
#     """
#     Sample data for the FrameBuilding object
#
#     :param fb:
#     :return:
#     """
#     number_of_storeys = 6
#     interstorey_height = 3.4  # m
#     masses = 40.0e3  # kg
#     n_bays = 3
#
#     fb = sfsimodels.FrameBuilding2D(number_of_storeys, n_bays)
#     fb.interstorey_heights = interstorey_height * np.ones(number_of_storeys)
#     fb.floor_length = 18.0  # m
#     fb.floor_width = 16.0  # m
#     fb.storey_masses = masses * np.ones(number_of_storeys)  # kg
#
#     fb.bay_lengths = [6., 6.0, 6.0]
#     fb.set_beam_prop("depth", [0.5, 0.5, 0.5], repeat="up")
#     fb.set_beam_prop("width", [0.4, 0.4, 0.4], repeat="up")
#     fb.set_column_prop("width", [0.5, 0.5, 0.5, 0.5], repeat="up")
#     fb.set_column_prop("depth", [0.5, 0.5, 0.5, 0.5], repeat="up")
#     fb.n_seismic_frames = 3
#     fb.n_gravity_frames = 0
#     return fb


def load_small_frame_building_sample_data():
    """
    Sample data for the FrameBuilding object

    :param fb:
    :return:
    """
    number_of_storeys = 1
    interstorey_height = 3.4  # m
    masses = 40.0e3  # kg
    n_bays = 1

    fb = sfsimodels.FrameBuilding2D(number_of_storeys, n_bays)
    fb.interstorey_heights = interstorey_height * np.ones(number_of_storeys)
    fb.floor_length = 18.0  # m
    fb.floor_width = 16.0  # m
    fb.storey_masses = masses * np.ones(number_of_storeys)  # kg

    fb.bay_lengths = [6.]
    fb.set_beam_prop("depth", [0.5], repeat="up")
    fb.set_beam_prop("width", [0.4], repeat="up")
    fb.set_column_prop("width", [0.5, 0.5], repeat="up")
    fb.set_column_prop("depth", [0.5, 0.5], repeat="up")
    return fb


if __name__ == '__main__':
    from tests import conftest
    record_filename = 'test_motion_dt0p01.txt'
    motion_step = 0.01
    rec = np.loadtxt(conftest.TEST_DATA_DIR + record_filename)

    xi = 0.05

    acc_signal = eqsig.AccSignal(rec, motion_step)
    time = acc_signal.time

    # frame = load_frame_building_sample_data()
    frame = load_small_frame_building_sample_data()
    print("Building loaded")

    outputs = get_inelastic_response(frame, rec, motion_step, xi=xi, extra_time=0)
    print("Analysis complete")
    acc_opensees = np.interp(time, outputs["time"], outputs["rel_accel"]) - rec
    ux_opensees = np.interp(time, outputs["time"], outputs["rel_disp"])
    plt.plot(ux_opensees)
    plt.show()
    print("Complete")
