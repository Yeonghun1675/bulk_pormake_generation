import os
from pathlib import Path
from itertools import tee
import glob

###############################
indir = '/home/users/kimjuneho4/foundation_mof/small'
outdir = '/home/users/kimjuneho4/foundation_mof/lammpterface/0_result/dataNin'
lammperface = '/home/users/kimjuneho4/anaconda3/envs/fmof/bin/lammps-interface'
NODE = '1'
NUM_QSUB = 60
NUM_CORE = 1
NODE_TYPE = 'ac'
#################################

indir = Path(indir).resolve()
outdir = Path(outdir)

if not indir.exists():
    raise ValueError(f'{str(indir)} does not exists()')

outdir.mkdir(exist_ok=True, parents=True)

# list_cifs, len_cifs = tee(indir.glob('*.cif'))
# len_cifs = sum([1 for _ in len_cifs])

n = len(list(indir.glob('*.cif'))) // NUM_QSUB

def write_qsub(path_cif:Path, N:int, outdir:Path=outdir):
    if (outdir/f'data.{path_cif.stem}').exists():
        return

    file = outdir/f'lammps_iterface_{N}.qsub'
    
    if not file.exists():
        with open(file, 'w') as f:
            f.write("#!/bin/sh\n")
            f.write("#PBS -r n\n")
            f.write("#PBS -q long\n")
            f.write(f"#PBS -l nodes={NODE}:ppn={NUM_CORE}:{NODE_TYPE}\n")
            f.write("cd $PBS_O_WORKDIR\n\n")

    with open(file, 'a') as f:
        f.write(f"{lammperface} --cutoff=6 {path_cif.absolute()} > /home/users/kimjuneho4/foundation_mof/lammpterface/0_result/tmp_log_{N}.out 2>&1\n")
        f.write(f"echo {path_cif} >> /home/users/kimjuneho4/foundation_mof/lammpterface/0_result/log_{N}.out\n")
        f.write(f"cat /home/users/kimjuneho4/foundation_mof/lammpterface/0_result/tmp_log_{N}.out >> /home/users/kimjuneho4/foundation_mof/lammpterface/0_result/log_{N}.out\n\n")

for i, path_cif in enumerate(indir.glob('*.cif')):
    N = i // n
    write_qsub(path_cif, N, outdir)
    
    

