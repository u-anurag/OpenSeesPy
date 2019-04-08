from openseespy.wrap.commands.uniaxial_materials.base_material import UniaxialMaterialBase


class Viscous(UniaxialMaterialBase):
    op_type = "Viscous"

    def __init__(self, osi, c, alpha):
        self.c = c
        self.alpha = alpha
        osi.n_mats += 1
        self._tag = osi.n_mats
        self._parameters = [self.op_type, self._tag, self.c, self.alpha]
        self.to_process()


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
        self.to_process()


class MultiLinear(UniaxialMaterialBase):
    op_type = "MultiLinear"

    def __init__(self, osi, points):
        self.points = points
        osi.n_mats += 1
        self._tag = osi.n_mats
        self._parameters = [self.op_type, self._tag, self.points]
        self.to_process()

