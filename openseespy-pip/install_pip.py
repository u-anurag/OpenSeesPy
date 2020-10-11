import subprocess

from build_pip import copy_library, build_pip, upload_pip, clean_pip

copy_library('../../opensees/SRC/interpreter/opensees.so',
             '../../opensees/SRC/interpreter/opensees.pyd')
build_pip()
upload_pip()
clean_pip()
