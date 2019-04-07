from openseespy.wrap.base_models import OpenseesObject


class SectionBase(OpenseesObject):
    op_base_type = "section"


class Elastic(SectionBase):
    op_type = "Elastic"

    def __init__(self, osi, e_mod, area, i_zz=None, g_mod=None, j_sect=None, alpha_y=0.0,
                 alpha_z=0.0):
        self.e_mod = e_mod
        self.area = area
        self.i_zz = i_zz
        self.g_mod = g_mod
        self.j_sect = j_sect
        self.alpha_y = alpha_y
        self.alpha_z = alpha_z
        osi.n_sects += 1
        self._tag = osi.n_sects

        self._parameters = [self.op_type, self._tag, self.e_mod, self.area, self.i_zz]
        if self.g_mod is not None:
            self._parameters.append(self.g_mod)
        if self.j_sect is not None:
            self._parameters.append(self.j_sect)
            self._parameters.append(self.alpha_y)
            self._parameters.append(self.alpha_z)
        self.to_process()
