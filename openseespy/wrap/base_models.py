import openseespy.opensees as opy
from openseespy.wrap import exceptions


class OpenseesObject(object):
    base_type = "<not-set>"  # used to call opensees module
    type = "<not-set>"  # string name given to object in opensees module
    _tag = None
    _name = None
    _parameters = None

    @property  # deliberately no setter method
    def tag(self):
        return self._tag

    @property
    def name(self):
        return self._name

    def to_process(self):
        try:
            return getattr(opy, self.base_type)(*self.parameters)
        except SystemError as e:
            if None in self.parameters:
                print(self.parameters)
                raise exceptions.ModelError("%s of type: %s contains 'None'" % (self.base_type, self.type))
            else:
                raise SystemError(e)
        except AttributeError as e:
            print(e)
            raise exceptions.ModelError("base_type: '%s' does not exist in opensees module" % self.base_type)

    def to_commands(self):
        para = []
        for i, e in enumerate(self.parameters):
            if isinstance(e, str):
                e = "'%s'" % e
            para.append(str(e))
            if i > 40:  # avoid verbose print output
                break
        p_str = ', '.join(para)
        return 'op.%s(%s)' % (self.base_type, p_str)

    @property
    def parameters(self):
        return self._parameters
