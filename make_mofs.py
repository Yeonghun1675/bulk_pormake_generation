import numpy as np
from pathlib import Path
from pormake import *

# Basic settings for accessing database of pormake
db = Database()

# Directory settings & validation
candidate_file = "./hmof_candidates.txt"
small_dir = "./small"
large_dir = "./large"

try:
    if not Path(candidate_file).resolve().exists():
        raise Exception('Error: hmof_candidates.txt file does not exist!')
except Exception as e:
    print(e)
    exit()

Path(small_dir).resolve().mkdir(exist_ok=True, parents=True)
Path(large_dir).resolve().mkdir(exist_ok=True, parents=True)

# Builder function
def name_to_mof(_mof_name):
    tokens = _mof_name.split("+")
    _topo_name = tokens[0]

    _node_bb_names = []
    _edge_bb_names = []
    for bb in tokens[1:]:
        if bb.startswith("N"):
            _node_bb_names.append(bb)

        if bb.startswith("E"):
            _edge_bb_names.append(bb)

    _topology = db.get_topo(_topo_name)
    _node_bbs = [db.get_bb(f'{n}.xyz') for n in _node_bb_names]
    _edge_bbs = {tuple(et): None if n == 'E0' else db.get_bb(f'{n}.xyz')
                 for et, n in zip(_topology.unique_edge_types, _edge_bb_names)}

    _builder = Builder()
    _mof = _builder.build_by_type(_topology, _node_bbs, _edge_bbs)

    return _mof

# Obtain hmof_candidates
with open(candidate_file, "r") as f:
    mof_names = f.read().split()

print("Start generation.")

# Generate all candidates
for name in mof_names:
    print(name, end=" ")

    try:
        mof = name_to_mof(name)

        if isinstance(mof, str):
            print(mof, ", skip.")
            continue

        min_cell_length = np.min(mof.atoms.cell.cellpar()[:3])
        if min_cell_length < 4.5:
            print("Too small cell. Skip.")
            continue

        max_cell_length = np.max(mof.atoms.cell.cellpar()[:3])
        if max_cell_length < 45.0:
            mof.write_cif("{}/{}.cif".format(small_dir, name))
            print("Success (small).")
        else:
            mof.write_cif("{}/{}.cif".format(large_dir, name))
            print("Success (large).")

    except Exception as e:
        print("Fails.", e)

print("End generation.")









