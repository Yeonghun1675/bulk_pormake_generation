import re
from tqdm import tqdm
from pathlib import Path
from itertools import tee

##  parameters  #################################################

src_dir = '/home/users/kimjuneho4/foundation_mof/qsub'
dest_dir = '/home/users/kimjuneho4/foundation_mof/qsub'

NUM_QSUB = 1
NODE = 'ac'

# NODE = 'bnode10'
# NUM_QSUB = 30
# NUM_CORE = 1
# NODE_TYPE = 'amd'

################################################################

src_dir = Path(src_dir)
dest_dir = Path(dest_dir)

assert src_dir.exists()

in_file_dir = dest_dir/'in_files'
log_dir = dest_dir/'log'
out_file_dir = dest_dir/'opt_lammps_data'

in_file_dir.mkdir(exist_ok=True, parents=True)
log_dir.mkdir(exist_ok=True, parents=True)
out_file_dir.mkdir(exist_ok=True, parents=True)

exe = \
"""
variable a loop 10
label loop

minimize 1.0e-6 1.0e-8 1000 10000
fix 1 all box/relax iso 0.0 vmax 0.001
minimize 1.0e-6 1.0e-8 1000 10000
unfix 1
thermo 1000

next a
jump SELF loop
run 0

compute 1 all pe
variable A equal c_1

thermo_style custom temp c_1
thermo 1
run 0

print "{}:$A" append energy.txt 

write_data           {}
"""

# 1. make in file 

in_files, len_files = tee(src_dir.glob('in.*'))
len_files = sum([1 for _ in len_files])

for in_file in tqdm(in_files, total=len_files):
    cif_id = in_file.suffix[1:]

    with open(in_file, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if 'read_data' in line:
            lines[i] = re.sub(r"data\.\S+", str((src_dir/f'data.{cif_id}').absolute()), line)

        if 'log.' in line:
            log_file = log_dir/f'log.{cif_id}'
            lines[i] = re.sub(r"log\.\S+", str(log_file.absolute()), line)


    new_in_file = in_file_dir/f'in.{cif_id}'
    with open(new_in_file, 'w') as f:
        for line in lines:
            f.write(line)
        w_file = out_file_dir/f'{cif_id}.lammps-data'
        f.write(exe.format(cif_id, str(w_file.absolute())))


# 2. make qsub file

def write_qsub(path_in:Path, N:int, outdir:Path, NODE:str=NODE):
    
    file = outdir/f'md_optimize_{N}.qsub'
    
    if not file.exists():
        with open(file, 'w') as f:
            f.write("#!/bin/sh\n")
            f.write("#PBS -r n\n")
            f.write("#PBS -q long\n")
            f.write(f"#PBS -l nodes=1:ppn=1:{NODE}\n")
            f.write("export OMP_NUM_THREADS=1\n")
            f.write("cd $PBS_O_WORKDIR\n\n")
            f.write("mpirun --mca mtl ^psm2,psm,ofi --mca orte_base_help_aggregate 0 –np 2\n")


    with open(file, 'a') as f:
        f.write(f"/opt/lammps/200303/bin/lmp_mpi -in {str(path_in.absolute())} 1>log/out_{N}.lammps 2>&1\n")

n = len_files // NUM_QSUB

for i, path_in in tqdm(enumerate(in_file_dir.glob('in.*')), total=len_files):
    N = i // n
    write_qsub(path_in, N, dest_dir)
