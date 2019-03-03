from openseespy.wrap.base_models import OpenseesObject


class TestBase(OpenseesObject):
    base_type = "test"


class EnergyIncr(TestBase):
    type = "EnergyIncr"

    def __init__(self, osi, tol, max_iter, p_flag=0, n_type=2):
        self.tol = float(tol)
        self.max_iter = int(max_iter)  # changed to avoid python function iter
        self.p_flag = int(p_flag)
        self.n_type = int(n_type)
        self._parameters = [self.type, self.tol, self.max_iter, self.p_flag, self.n_type]
        self.to_process()
