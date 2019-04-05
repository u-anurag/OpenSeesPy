from openseespy.wrap.commands.materials.base_material import UniaxialMaterial


class UniaxialViscous(UniaxialMaterial):
    op_type = "Viscous"

    def __init__(self, osi, c, alpha):
        self.c = c
        self.alpha = alpha
        osi.n_mats += 1
        self._tag = osi.n_mats
        self._parameters = [self.op_type, self._tag, self.c, self.alpha]
        self.to_process()


class UniaxialMultiLinear(UniaxialMaterial):
    op_type = "MultiLinear"

    def __init__(self, osi, points):
        self.points = points
        osi.n_mats += 1
        self._tag = osi.n_mats
        self._parameters = [self.op_type, self._tag, self.points]
        self.to_process()

