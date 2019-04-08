import openseespy.opensees as opy


class OpenseesInstance(object):
    n_nodes = 0
    n_cons = 0
    n_eles = 0
    n_mats = 0
    n_sects = 0
    n_tseries = 0
    n_pats = 0
    n_fixs = 0
    n_integs = 0
    n_transformations = 0

    def __init__(self, dimensions: int):
        self.dimensions = dimensions
        opy.wipe()
        opy.model('basic', '-ndm', dimensions, '-ndf', 3)  # 2 dimensions, 3 dof per node
