from openseespy.wrap.base_models import OpenseesObject


class AlgorithmBase(OpenseesObject):
    base_type = "op_algorithm"


class Linear(AlgorithmBase):
    type = "Linear"

    def __init__(self, osi, secant=False, initial=False, factor_once=False):
        self.secant = secant
        self.initial = initial
        self.factor_once = factor_once
        self._parameters = [self.type, self.secant, self.initial, self.factor_once]
        self.to_process()


class Newton(AlgorithmBase):
    type = "Newton"

    def __init__(self, osi, secant=False, initial=False, initial_then_current=False):
        self.secant = secant
        self.initial = initial
        self.initial_then_current = initial_then_current
        self._parameters = [self.type, self.secant, self.initial, self.initial_then_current]
        self.to_process()
