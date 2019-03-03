from openseespy.wrap.base_models import OpenseesObject


class Rayleigh(OpenseesObject):
    base_type = "op_rayleigh"
    type = "rayleigh"

    def __init__(self, osi, alpha_m, beta_k, beta_k_init, beta_k_comm):
        """
        Assign Rayleigh damping to previously defined nodes

        Parameters
        ----------
        osi
        alpha_m : float
            factor applied to elements or nodes mass matrix
        beta_k : float
            factor applied to elements current stiffness matrix
        beta_k_init : float
            factor applied to elements initial stiffness matrix
        beta_k_comm : float
            factor applied to elements committed stiffness matrix
        """
        self.alpha_m = float(alpha_m)
        self.beta_k = float(beta_k)
        self.beta_k_init = float(beta_k_init)
        self.beta_k_comm = float(beta_k_comm)
        self._parameters = [self.alpha_m, self.beta_k, self.beta_k_init, self.beta_k_comm]
        self.to_process()

