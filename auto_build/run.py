import re

w8 = '        '

def constructor(base_type, op_type, params, dtypes):
    para = []
    para.append(f'class {op_type}({base_type[0].capitalize() + base_type[1:]}Base):')
    para.append('')
    pms = [pm.lower() for pm in params]
    if 'tag' in pms[0]:
        pms = pms[1:]
    pjoined = ', '.join(pms)
    para.append(f'    def __init__(self, osi, {pjoined}):')
    for i, pm in enumerate(pms):
        if dtypes[i] == 'float':
            para.append(f'        self.{pm} = float({pm})')
        elif dtypes[i] == 'int':
            para.append(f'        self.{pm} = int({pm})')
        else:
            para.append(f'        self.{pm} = {pm}')
    para.append(w8 + 'osi.n_mats += 1')
    para.append(w8 + 'self._tag = osi.mats')
    para.append(w8 + 'self._parameters = [self.op_type, self._tag, self.%s]' % (', self.'.join(pms)))
    para.append(w8 + 'self.to_process(osi)')
    return '\n'.join(para)

def parse_file(ffp):
    a = open(ffp)
    lines = a.read().split('\n')
    params = []
    dtypes = []
    base_type = None
    for line in lines:
        pname_pat = '\``([A-Za-z0-9_\./\\-]*)\``'
        res = re.search(pname_pat, line)
        if res:
            print(res.group()[2:-2])
            params.append(res.group()[2:-2])
            dtype_pat = '\|([A-Za-z0-9_\./\\-]*)\|'
            dtype_res = re.search(dtype_pat, line)
            print(dtype_res.group())
            dtype = dtype_res.group()[1:-1]
            dtypes.append(dtype)
        if base_type is None and '.. function:: ' in line:
            print(line)
            base_type = line.split('.. function:: ')[-1]
            base_type = base_type.split('(')[0]
            optype_pat = "\'([A-Za-z0-9_\./\\-]*)\'"
            optype_res = re.search(optype_pat, line)
            optype = optype_res.group()[1:-1]
            print(optype_res)

    pstr = constructor(base_type, optype, params, dtypes)
    print(pstr)
    # if line[3:5] == '``':
    #     para = line[5:]


if __name__ == '__main__':
    parse_file('BoucWen.rst')