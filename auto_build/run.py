import docutils.frontend
import docutils.parsers.rst
import re
from collections import OrderedDict


w4 = '    '
w8 = '        '
pname_pat = '\``([A-Za-z0-9_\./\\\'-]*)\``'
dtype_pat = '\|([A-Za-z0-9_\./\\-]*)\|'
optype_pat = "\'([A-Za-z0-9_\./\\-]*)\'"


def clean_param_names(params):
    pms = OrderedDict()
    for pm in params:
        new_pm = pm
        dtype_is_obj = False
        if len(pm) == 1 and pm.istitle():
            new_pm = 'big_' + pm.lower()
        else:
            new_pm = convert_camel_to_snake(pm)

        if len(new_pm) > 4 and new_pm[-4:] == '_tag':
            new_pm = new_pm[:-4]
            dtype_is_obj = True
        pms[new_pm] = params[pm]
        if dtype_is_obj:
            pms[new_pm].dtype = 'obj'
        pms[new_pm].o3_name = new_pm
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


def constructor(base_type, op_type, defaults, w_op_kwargs):
    para = []
    op_class_name = convert_name_to_class_name(op_type)
    base_class_name = base_type[0].capitalize() + base_type[1:]
    para.append(f'class {op_class_name}({base_class_name}Base):')
    para.append('')

    pms = clean_param_names(defaults)
    pjoins = []
    for pm in pms:
        default = pms[pm].default_value
        if default is not None:
            if pms[pm].default_is_expression:
                pjoins.append(f'{pm}=None')
            else:  # TODO: deal with w_op_kwargs
                pjoins.append(f'{pm}={default}')
        else:
            pjoins.append(f'{pm}')

    pjoined = ', '.join(pjoins)
    para.append(f'    def __init__(self, osi, {pjoined}):')
    for i, pm in enumerate(pms):
        dtype = pms[pm].dtype
        if dtype == 'float':
            para.append(w8 + f'self.{pm} = float({pm})')
        elif dtype == 'int':
            para.append(w8 + f'self.{pm} = int({pm})')
        else:
            para.append(w8 + f'self.{pm} = {pm}')
    para.append(w8 + 'osi.n_mats += 1')
    para.append(w8 + 'self._tag = osi.mats')
    pjoins = []
    need_special_logic = False
    for pm in pms:
        if pms[pm].default_is_expression:
            need_special_logic = True
            break
        if pms[pm].dtype == 'obj':
            pjoins.append(f'self.{pm}.tag')
        elif pms[pm].packed:
            pjoins.append('*self.' + pm)
        else:
            pjoins.append('self.' + pm)
    para.append(w8 + 'self._parameters = [self.op_type, self._tag, self.%s]' % (', '.join(pjoins)))
    if need_special_logic:
        sp_logic = False
        sp_pms = []
        for pm in pms:
            if pms[pm].default_is_expression:
                sp_logic = True
            if sp_logic:
                sp_pms.append("'%s'" % pm)
        para.append(w8 + f"special_pms = [{', '.join(sp_pms)}]")
        para.append(w8 + 'for pm in special_pms:')
        para.append(w8 + w4 + 'if getattr(self, pm) is not None:')
        para.append(w8 + w8 + 'self._parameters += [getattr(self, pm)]')
    para.append(w8 + 'self.to_process(osi)')

    low_op_name = convert_camel_to_snake(op_class_name)
    low_base_name = convert_camel_to_snake(base_class_name)

    # Build test
    para.append('')
    para.append(f'def test_{low_op_name}():')
    para.append(w4 + 'osi = opw.OpenseesInstance(dimensions=2)')
    pjoins = []
    for i, pm in enumerate(pms):
        default = pms[pm].default_value
        dtype = pms[pm].dtype
        if default is not None:
            pjoins.append(f'{pm}={default}')
        elif dtype == 'float':
            pjoins.append(f'{pm}=1.0')
        elif dtype == 'obj':
            pjoins.append(f'{pm}=obj')
        else:
            pjoins.append(f'{pm}=1')
    pjoint = ', '.join(pjoins)
    para.append(w4 + f'opw.{low_base_name}.{op_class_name}(osi, {pjoint})')
    return '\n'.join(para)


class Param(object):
    def __init__(self, org_name, default_value, packed=None, dtype=None):
        self.org_name = org_name
        self.o3_name = None
        self.default_value = default_value
        self.packed = packed
        self.dtype = dtype
        self.default_is_expression = False
        self.p_description = ''


def check_if_default_is_expression(defo):
    if any(re.findall('|'.join(['\*', '\/', '\+', '\-', '\^']), defo)):
        return True
    return False


def clean_fn_line(line):
    defaults = OrderedDict()
    print(line)
    base_type = line.split('.. function:: ')[-1]
    base_type = base_type.split('(')[0]
    optype_res = re.search(optype_pat, line)
    optype = optype_res.group()[1:-1]
    print(optype_res)
    inputs_str = line.split(')')[0]
    inputs = inputs_str.split(',')
    inputs = inputs[2:]  # remove class definition and tag
    op_kwargs = OrderedDict()
    w_op_kwargs = None  # if function has strings to enter keyword args
    cur_kwarg = None
    for inpy in inputs:
        inpy = inpy.replace(' ', '')
        if '=' in inpy:
            inp, defo = inpy.split('=')
        else:
            inp = inpy
            defo = None
        if '-' in inp:
            cur_kwarg = inp[1:]
            op_kwargs[cur_kwarg] = []
            # continue
        if inp[0] == '*':
            inp = inp[1:]
            packed = True
        else:
            packed = False
        if inp in defaults:
            i = 2
            new_inp = inp + '_%i' % i
            while new_inp in defaults:
                i += 1
                new_inp = inp + '_%i' % i
        else:
            new_inp = inp
        defaults[new_inp] = Param(org_name=inp, default_value=defo, packed=packed)
        if defo is not None and check_if_default_is_expression(defo):
            defaults[inp].default_is_expression = True
        if cur_kwarg is not None:
            op_kwargs[cur_kwarg].append(inp)
    return base_type, optype, defaults, w_op_kwargs


def parse_mat_file(ffp):
    a = open(ffp)
    lines = a.read().split('\n')
    doc_str_pms = []
    dtypes = []
    defaults = None
    base_type = None
    optype = None
    w_op_kwargs = False
    descriptions = []
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
            ei = line.find('|')
            dtype_res = re.search(dtype_pat, line)
            if dtype_res is None:
                continue
            print(dtype_res.group())
            dtype = dtype_res.group()[1:-1]
            print(dtype_res.end())
            des = line[dtype_res.end():]
            des = des.replace('\t', ' ')
            while des[0] == ' ':
                des = des[1:]
                if not len(des):
                    break
            descriptions.append(des)
            res = re.findall(pname_pat, line[:ei])
            for pm in res:
                doc_str_pms.append(pm)
                dtypes.append(dtype)
        if base_type is None and '.. function:: ' in line:
            base_type, optype, defaults, w_op_kwargs = clean_fn_line(line)
    doc_str_pms = doc_str_pms[1:]  # remove mat tag
    dtypes = dtypes[1:]
    print(doc_str_pms)
    print(list(defaults))
    assert len(doc_str_pms) == len(defaults), (len(doc_str_pms), len(defaults))
    for i, pm in enumerate(doc_str_pms):
        defaults[pm].dtype = dtypes[i]
        defaults[pm].p_description = descriptions[i]

    pstr = constructor(base_type, optype, defaults, w_op_kwargs)
    print(pstr)
    return pstr
    # if line[3:5] == '``':
    #     para = line[5:]


def parse_all_uniaxial_mat():
    import user_paths as up
    uni_axial_mat_file = open(up.OPY_DOCS_PATH + 'uniaxialMaterial.rst')
    lines = uni_axial_mat_file.read().split('\n')
    collys = {}
    mtype = None
    for line in lines:
        if ':caption: Steel & Reinforcing-Steel Materials' in line:
            mtype = 'steel'
            collys[mtype] = []
            continue
        if ':caption: Concrete Materials' in line:
            mtype = 'concrete'
            collys[mtype] = []
            continue
        if ':caption: Standard Uniaxial Materials' in line:
            mtype = 'standard'
            collys[mtype] = []
            continue
        if ':caption: PyTzQz uniaxial materials' in line:
            mtype = 'pytz'
            collys[mtype] = []
            continue
        if ':caption: Other Uniaxial Materials' in line:
            mtype = 'other'
            collys[mtype] = []
            continue
        if mtype is not None:
            line = line.replace(' ', '')
            line = line.replace('\t', '')
            if 'toctree' in line or 'maxdepth' in line or line =='':
                continue
            collys[mtype].append(line)
    for item in collys:
        para = ['from openseespy.wrap.command.uniaxial_material.base_material import UniaxialMaterialBase', '', '']
        print(item, collys[item])
        for mat in collys[item]:
            if mat == 'steel4':
                continue
            open(up.OPY_DOCS_PATH + '%s.rst' % mat)
            ffp = up.OPY_DOCS_PATH + '%s.rst' % mat
            parse_mat_file(ffp)



if __name__ == '__main__':
    # parse_mat_file('BoucWen.rst')
    # parse_mat_file('Bond_SP01.rst')
    import user_paths as up
    parse_mat_file(up.OPY_DOCS_PATH + 'ReinforcingSteel.rst')
    # parse_all_uniaxial_mat()
    # defo = 'a2*k'
    # if any(re.findall('|'.join(['\*', '\/', '\+', '\-', '\^']), defo)):
    #     print('found')