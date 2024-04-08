import pickle
import random
import numpy as np
from itertools import chain
from pathlib import Path
from pormake import *

# Basic settings for accessing database of pormake
db = Database()

### IMPORTANT: Serialization of database ###
### It is a MANDATORY STEP for using topology data in PORMAKE module!
### You only need to execute this step ONCE! (This step takes some time!)
### After execution, ensure that the .pickle files are created in the directory (/(YOUR_DIRECTORY)/PORMAKE/pormake/database/topologies/*.pickle)
### Also, some topology.pickle files cannot be generated => You can check the failed topology list in the terminal (RECOMMEND: save the failed topology list for later)

# ↓↓↓↓↓↓↓↓↓↓↓↓ #
# db.serialize()
# ↑↑↑↑↑↑↑↑↑↑↑↑ #
failed_topo = ['ibb', 'mmo', 'css', 'tfy-a', 'elv', 'tsn', 'lcz', 'xbn', 'dgo', 'ten', 'scu-h', 'zim', 'ild', 'cds-t', 'crt', 'jsm', 'rht-x', 'mab', 'ddi', 'mhq', 'nbo-x', 'tcb', 'zst', 'she-d', 'ffg-a', 'cdh', 'ast-d', 'ffj-a', 'ddy', 'llw-z', 'tpt', 'utx', 'fnx', 'roa', 'nia-d', 'dnf-a', 'lcw_component_3', 'baz-a', 'yzh', 'dia-x']

# Topology info
# 1. for specific topologies
# topo = ['pcu', 'tbo']
# 2. for all topologies
topo = db._get_topology_list()
topo = list(set(topo).difference(set(failed_topo)))

# Node info
# Last update (24.04)
# NOTICE: The information of failed topologies is not included!
# Dictionary format: {'topology name(str)':'list of RMSD-CALCULATED nodes for the given topology(list[list[], ... ])'}
# Criterion: rmsd <= 0.3
# Change the directory of topology_with_rmsd_calculated_node.pickle file if necessary
node_path = './data/topology_with_rmsd_calculated_node.pickle'

try:
    if not Path(node_path).resolve().exists():
        raise Exception('Error: topology_with_rmsd_caculated_node.pickle does not exist!')
except Exception as e:
    print(e)
    exit()
        
node = dict()
with open(node_path, 'rb') as a:
    node = pickle.load(a)

# Edge info

edge = [f for f in db._get_bb_list() if f.startswith('E')] + ['E0']

##############################################
########## Conditions for your hMOF ##########
########## ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ ##########

max_n_atoms = 1000      # How many atoms do hMOFs have at most?
target_n_mofs = 10      # How many hMOFS do you want to generate?
hmof_candidates = []

########## ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ ##########
########## Conditions for your hMOF ##########
##############################################

# Helper function for counting atoms in each building block (i.e. node, edge)
def count_atoms_in_bb(bb:BuildingBlock):
    if bb is None:
        return 0
    else:
        return np.sum(bb.atoms.get_chemical_symbols() != np.array('X'))
    
# Helper function for counting atoms in hmof
def calculate_n_atoms_of_mof(topo:Topology, nodes:dict, edges:dict):
    nt_counts = {}
    for nt in topo.unique_node_types:
        n_nt = np.sum(topo.node_types == nt)
        nt_counts[nt] = n_nt

    et_counts = {}
    for et in topo.unique_edge_types:
        n_et = np.sum(np.all(topo.edge_types == et[np.newaxis, :], axis=1))
        et_counts[tuple(et)] = n_et

    counts = 0
    for nt, node in nodes.items():
        counts += nt_counts[nt] * count_atoms_in_bb(node)

    for et, edge in edges.items():
        counts += et_counts[et] * count_atoms_in_bb(edge)

    return counts

# Helper function for making name of hmof
def make_mof_name(topo:Topology, nodes:dict, edges:dict):
    en = lambda x: x.name if x else "E0"
    
    node_names = [bb.name for bb in nodes.values()]
    edge_names = [en(bb) for bb in edges.values()]
    name = "+".join(
        [topo.name] + node_names + edge_names
    )
    return name

# Generate hMOFs
while len(hmof_candidates) < target_n_mofs:
    # Choose random topology
    _topo_name = random.sample(topo, 1)[0]
    _topo = db.get_topo(_topo_name)

    # Check node validation (Some nodes of topology is empty because of rmsd_value) 
    is_Valid = True
    for node_info in node[_topo_name]:
        if node_info == []:
            is_Valid = False
            break
    
    if not is_Valid:
        continue

    # Choose random node & edge for the given topology
    _node = {k: db.get_bb(random.sample(v, 1)[0]) for k, v in zip(_topo.unique_node_types, node[_topo_name])}
    _edge = {}
    for k in _topo.unique_edge_types:
        random_edge = random.sample(edge, 1)[0]
        if random_edge != 'E0':
            _edge[tuple(k)] = db.get_bb(random_edge)
        else:
            _edge[tuple(k)] = None

    # Check MOF
    is_MOF = False
    for _bb in chain(_node.values(), _edge.values()):
        if _bb is None:
            continue

        if _bb.has_metal:
            is_MOF = True
            break
            
    if not is_MOF:
        continue

    # Check the number of atoms
    n_atoms = calculate_n_atoms_of_mof(_topo, _node, _edge)
    if n_atoms > max_n_atoms:
        continue
    
    mof_name = make_mof_name(_topo, _node, _edge)

    # Check duplication
    if mof_name in hmof_candidates:
        continue

    # Add hmof candidates
    hmof_candidates.append(mof_name)

# Save your hmof in a txt file
# Change the directory if necessary
with open('./hmof_candidates.txt', 'w') as f:
    for hmof in hmof_candidates:
        f.write(f'{hmof}\n')