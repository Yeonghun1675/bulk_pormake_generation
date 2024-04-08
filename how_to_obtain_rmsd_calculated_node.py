import pickle
from pormake import *

# Basic settings for accessing database of pormake
db = Database()

# Node information
bbs = db._get_bb_list()
node_bbs = [f for f in bbs if f.startswith('N')]

# Topology information
topos = db._get_topology_list()
failed_topo = ['ibb', 'mmo', 'css', 'tfy-a', 'elv', 'tsn', 'lcz', 'xbn', 'dgo', 'ten', 'scu-h', 'zim', 'ild', 'cds-t', 'crt', 'jsm', 'rht-x', 'mab', 'ddi', 'mhq', 'nbo-x', 'tcb', 'zst', 'she-d', 'ffg-a', 'cdh', 'ast-d', 'ffj-a', 'ddy', 'llw-z', 'tpt', 'utx', 'fnx', 'roa', 'nia-d', 'dnf-a', 'lcw_component_3', 'baz-a', 'yzh', 'dia-x']
topos = list(set(topos).difference(set(failed_topo)))

# Dictionary for the final result
topo_dict = {}

# Rmsd calculation (This step is time-consuming)
for topo_name in topos:
    # Obtain topology
    topo = db.get_topo(topo_name)
    
    # Record rmsd_calculated node
    total = []

    for i, connection_point in enumerate(topo.unique_cn):
        # Obtain node candidates of proper coordination number
        node_candidates = []
        for node_bb in node_bbs:
            node = db.get_bb(node_bb)
            if node.n_connection_points == connection_point:
                node_candidates.append(node_bb)

        # rmsd calculation
        loc = Locator()

        for node_bb in node_candidates:
            bb_xyz = db.get_bb(node_bb)
            rmsd = loc.calculate_rmsd(topo.unique_local_structures[i], bb_xyz)

            if rmsd > 0.3:
                node_candidates.remove(node_bb)

        total.append(node_candidates)

    topo_dict[topo_name] = total

with open('./data/topology_with_rmsd_calculated_node.pickle', 'wb') as f:
    pickle.dump(topo_dict, f)











