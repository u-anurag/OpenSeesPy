from openseespy.wrap.base_models import OpenseesObject


class SystemBase(OpenseesObject):
    op_base_type = "system"


class ProfileSPD(SystemBase):
    op_type = "ProfileSPD"

    def __init__(self, osi):

        self._parameters = [self.op_type]
        self.to_process(osi)
