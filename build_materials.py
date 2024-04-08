import numpy as np
from pathlib import Path
import argparse
import pormake as pm
#from pormake import *

pm.log.disable_print()
pm.log.disable_file_print()  


# Builder function
def name_to_mof(_mof_name, db):
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

    _builder = pm.Builder()
    _mof = _builder.build_by_type(_topology, _node_bbs, _edge_bbs)

    return _mof


def build_materials(candidate_file, bb_dir=None, topo_dir=None, save_dir='small/', large_dir='large/'):
    # Basic settings for accessing database of pormake
    db = pm.Database(bb_dir=bb_dir, topo_dir=topo_dir)

    # Directory settings & validation
    #candidate_file = "./hmof_candidates.txt"
    #save_dir = "./small"
    #large_dir = "./large"

    try:
        if not Path(candidate_file).resolve().exists():
            raise Exception('Error: hmof_candidates.txt file does not exist!')
    except Exception as e:
        print(e)
        exit()

    Path(save_dir).resolve().mkdir(exist_ok=True, parents=True)
    Path(large_dir).resolve().mkdir(exist_ok=True, parents=True)


    # Obtain hmof_candidates
    with open(candidate_file, "r") as f:
        mof_names = f.read().split()

    print("Start generation.")

    # Generate all candidates
    for name in mof_names:
        print(name, end=" ")

        try:
            mof = name_to_mof(name, db)

            if isinstance(mof, str):
                print(mof, ", skip.")
                continue

            min_cell_length = np.min(mof.atoms.cell.cellpar()[:3])
            if min_cell_length < 4.5:
                print("Too small cell. Skip.")
                continue

            max_cell_length = np.max(mof.atoms.cell.cellpar()[:3])
            if max_cell_length < 45.0:
                mof.write_cif("{}/{}.cif".format(save_dir, name))
                print("Success (small).")
            else:
                mof.write_cif("{}/{}.cif".format(large_dir, name))
                print("Success (large).")

        except Exception as e:
            print("Fails.", e)

    print("End generation.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='make candidates'
    )
    parser.add_argument('-c', '--candidates', '--candidate-file', default=None)
    parser.add_argument('-b', '--bb-dir', '--building-block-dir', default=None)
    parser.add_argument('-t', '--topo-dir', '--topology-dir', default=None)


    args = parser.parse_args()

    build_materials(
        candidate_file=args.candidates, 
        bb_dir=args.bb_dir, 
        topo_dir=args.topo_dir
    )







