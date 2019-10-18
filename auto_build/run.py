import docutils.frontend
import docutils.parsers.rst
import re
from collections import OrderedDict


w4 = '    '
w8 = '        '
pname_pat = '\``([A-Za-z0-9_\./\\-]*)\``'
dtype_pat = '\|([A-Za-z0-9_\./\\-]*)\|'
optype_pat = "\'([A-Za-z0-9_\./\\-]*)\'"

def clean_params(params):
    pms = OrderedDict()
    for pm in params:
        new_pm = pm
        if len(pm) == 1 and pm.istitle():
            new_pm = 'big_' + pm.lower()
        # pms.append(pm.lower())
        new_pm = convert_camel_to_snake(pm)
        pms[new_pm] = params[pm]
    # if 'tag' in pms[0]:
    #     pms = pms[1:]
    return pms


def convert_name_to_class_name(name):
    name = name[0].capitalize() + name[1:]
    name = name.replace('_', '')
    return name


def convert_camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def constructor(base_type, op_type, doc_str_pms, dtypes, defaults):
    para = []
    op_class_name = convert_name_to_class_name(op_type)
    base_class_name = base_type[0].capitalize() + base_type[1:]
    para.append(f'class {op_class_name}({base_class_name}Base):')
    para.append('')
    for i, pm in enumerate(doc_str_pms):
        defaults[pm].append(dtypes[i])

    pms = clean_params(defaults)
    pjoins = []
    for pm in pms:
        default = pms[pm][0]
        if default is not None:
            pjoins.append(f'{pm}={default}')
        else:
            pjoins.append(f'{pm}')

    pjoined = ', '.join(pjoins)
    para.append(f'    def __init__(self, osi, {pjoined}):')
    for i, pm in enumerate(pms):
        dtype = pms[pm][1]
        if dtype == 'float':
            para.append(w8 + f'self.{pm} = float({pm})')
        elif dtype == 'int':
            para.append(w8 + f'self.{pm} = int({pm})')
        else:
            para.append(w8 + f'self.{pm} = {pm}')
    para.append(w8 + 'osi.n_mats += 1')
    para.append(w8 + 'self._tag = osi.mats')
    para.append(w8 + 'self._parameters = [self.op_type, self._tag, self.%s]' % (', self.'.join(pms)))
    para.append(w8 + 'self.to_process(osi)')

    low_op_name = convert_camel_to_snake(op_class_name)
    low_base_name = convert_camel_to_snake(base_class_name)
    para.append('')
    para.append(f'def test_{low_op_name}():')
    para.append(w4 + 'osi = opw.OpenseesInstance(dimensions=2)')
    pjoins = []
    for i, pm in enumerate(pms):
        default = pms[pm][0]
        dtype = pms[pm][1]
        if default is not None:
            pjoins.append(f'{pm}={default}')
        elif dtype == 'float':
            pjoins.append(f'{pm}=1.0')
        else:
            pjoins.append(f'{pm}=1')
    pjoint = ', '.join(pjoins)
    para.append(w4 + f'opw.{low_base_name}.{op_class_name}(osi, {pjoint})')
    return '\n'.join(para)


def parse_mat_file(ffp):
    a = open(ffp)
    lines = a.read().split('\n')
    doc_str_pms = []
    dtypes = []
    defaults = OrderedDict()
    base_type = None
    for line in lines:
        char_only = line.replace(' ', '')
        char_only = char_only.replace('\t', '')
        if not len(char_only):
            continue
        first_char = char_only[0]
        if first_char == '*':
            continue
        res = re.search(pname_pat, line)
        if res:
            print('pname: ', res.group()[2:-2])
            doc_str_pms.append(res.group()[2:-2])

            dtype_res = re.search(dtype_pat, line)
            print(dtype_res.group())
            dtype = dtype_res.group()[1:-1]
            dtypes.append(dtype)
        if base_type is None and '.. function:: ' in line:
            print(line)
            base_type = line.split('.. function:: ')[-1]
            base_type = base_type.split('(')[0]
            optype_res = re.search(optype_pat, line)
            optype = optype_res.group()[1:-1]
            print(optype_res)
            inputs_str = line.split(')')[0]
            inputs = inputs_str.split(',')
            inputs = inputs[2:]  # remove class definition and tag
            for inpy in inputs:
                inpy = inpy.replace(' ', '')
                if '=' in inpy:
                    inp, defo = inpy.split('=')
                else:
                    inp = inpy
                    defo = None
                defaults[inp] = [defo]
    doc_str_pms = doc_str_pms[1:]  # remove mat tag
    dtypes = dtypes[1:]
    pstr = constructor(base_type, optype, doc_str_pms, dtypes, defaults)
    print(pstr)
    # if line[3:5] == '``':
    #     para = line[5:]


if __name__ == '__main__':
    # parse_mat_file('BoucWen.rst')
    # parse_mat_file('Bond_SP01.rst')
    parse_mat_file('InitStrainMaterial.rst')