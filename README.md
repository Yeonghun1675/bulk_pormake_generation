<div align="center">

<h1> 💻 Bulk Pormake Generation </h1>

  <p>
    <strong>Bulk generation of porous material with pormake</strong>
  </p>

</div>

## 1. Installation
```bash
# install pormake
$ pip install pormake

# download bulk pormake generation
$ git clone https://github.com/Yeonghun1675/bulk_pormake_generation.git
```

## 2. Generate pre-defined building block list
```bash
# make pre-defined building block list
$ python rmsd_calculated_node.py --save=YOUR_SAVE_PATH

# make pre-defined building block list with custom bulding blocks and topologies
$ python rmsd_calculated_node.py --bb-dir=YOUR_BB_DIR --topo-dir=YOUR_TOPO_DIR --save=YOUR_SAVE_PATH 
```
- `save` is the name of the file where the list of pre-defined building blocks will be saved. (default: data/rmsd_calculated_node.pickle)


## 3. Make candidate list
```bash
# make candidate list
$ python make_candidates.py -n=1000 --pre-defined-list=YOUR_PRE_DEFINED_LIST --save=YOUR_SAVE_PATH

# make candidate list with custom building blocks and topologies
$ python make_candidates.py -n=1000 --pre-defined-list=YOUR_PRE_DEFINED_LIST --save=YOUR_SAVE_PATH --topo-dir=YOUR_TOPO_DIR --bb-dir=YOUR_BB_DIR 
```
- `pre_defined-list` is the name of the file where the list of pre-defined building blocks saved. (default: data/rmsd_calculated_node.pickle)
- `save` is the name of the file where the list of candidate will be saved (default: hmof_candidates.txt)
- `n` or `target_n_mofs` is number of materials


## 4. Build materials
```bash
# build materials
$ python build_materials.py --candidates=YOUR_CANDIDATE_LIST --save-dir=YOUR_SAVE_DIR

# build materials with custom building blocks and topologies
$ python build_materials.py --candidates=YOUR_CANDIDATE_LIST --save-dir=YOUR_SAVE_DIR --topo-dir=YOUR_TOPO_DIR --bb-dir=YOUR_BB_DIR 
```

## 5. Optimize materials using LAMMPS (optional)
```bash
$ cd optimize/
$ python 0_make_lammps_interface.py
$ python 1_make_optimize_qsub.py
$ python 2_convert_lammps_data.py
```


## Citation
If you want to cite bulk porous materials, please refer to the following paper:

1. Computational Screening of Trillions of Metal–Organic Frameworks for High-Performance Methane Storage, ACS Appl. Mater. Interfaces 2021, 13, 20, 23647–23654. [link](https://doi.org/10.1021/acsami.1c02471)

2. Enhancing Structure–Property Relationships in Porous Materials through Transfer Learning and Cross-Material Few-Shot Learning, ACS Appl. Mater. Interfaces 2023, 15, 48, 56375–56385. [link](https://doi.org/10.1021/acsami.3c10323)

