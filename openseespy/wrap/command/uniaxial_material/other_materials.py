from openseespy.wrap.command.uniaxial_material.base_material import UniaxialMaterialBase


class Viscous(UniaxialMaterialBase):
    op_type = "Viscous"

    def __init__(self, osi, c, alpha):
        self.c = c
        self.alpha = float(alpha)
        osi.n_mats += 1
        self._tag = osi.n_mats
        self._parameters = [self.op_type, self._tag, self.c, self.alpha]
        self.to_process(osi)


class ElasticBiLinear(UniaxialMaterialBase):
    op_type = "ElasticBilin"

    def __init__(self, osi, ep1, ep2, eps_p2, en1=None, en2=None, eps_n2=None):
        """

        Parameters
        ----------
        osi : opensees_pack.opensees_instance.OpenseesInstance object
            An instance of opensees
        ep1
        ep2
        eps_p2
        en1
        en2
        eps_n2
        """

        self.ep1 = ep1
        self.ep2 = ep2
        self.eps_p2 = eps_p2
        self.en1 = en1
        self.en2 = en2
        self.eps_n2 = eps_n2
        osi.n_mats += 1
        self._tag = osi.n_mats
        self._parameters = [self.op_type, self._tag, self.ep1, self.ep2, self.eps_p2]
        if self.en1 is not None:
            self._parameters += [self.en1, self.en2, self.eps_n2]
        self.to_process(osi)


class MultiLinear(UniaxialMaterialBase):
    op_type = "MultiLinear"

    def __init__(self, osi, points):
        self.points = points
        osi.n_mats += 1
        self._tag = osi.n_mats
        self._parameters = [self.op_type, self._tag, self.points]
        self.to_process(osi)


class BoucWen(UniaxialMaterialBase):

    def __init__(self, osi, alpha, ko, n, gamma, ao, deltanu):
        self.alpha = int(alpha)
        self.ko = float(ko)
        self.n = float(n)
        self.gamma = float(gamma)
        self.ao = float(ao)
        self.deltanu = float(deltanu)
        osi.n_mats += 1
        self._tag = osi.mats
        self._parameters = [self.op_type, self._tag, self.alpha, self.ko, self.n, self.gamma, self.ao, self.deltanu]
        self.to_process(osi)


class BondSP01(UniaxialMaterialBase):

    def __init__(self, osi, fy, sy, fu, su, b, big_r):
        self.fy = int(fy)
        self.sy = float(sy)
        self.fu = float(fu)
        self.su = float(su)
        self.b = float(b)
        self.big_r = float(big_r)
        osi.n_mats += 1
        self._tag = osi.mats
        self._parameters = [self.op_type, self._tag, self.fy, self.sy, self.fu, self.su, self.b, self.big_r]
        self.to_process(osi)
