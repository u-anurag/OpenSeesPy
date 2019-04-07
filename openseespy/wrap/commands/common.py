import openseespy.opensees as opy


def set_node_mass(node, x_mass, y_mass, rot_mass):
    opy.mass(node.tag, x_mass, y_mass, rot_mass)


def set_equal_dofs(node_1, node_2, dof):
    opy.equalDOF(node_1.tag, node_2.tag,  dof)


def set_node_fixities(node, x, y, z_rot, z=None, x_rot=None, y_rot=None):

    opy.fix(node.tag, x, y, z_rot)  # TODO: is order correct? deal with 3D
