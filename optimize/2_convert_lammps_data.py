from pathlib import Path
from itertools import tee
from tqdm import tqdm

#############################
path = '/home/users/kimjuneho4/foundation_mof/qsub/opt_lammps_data'
outdir = '/home/users/kimjuneho4/foundation_mof/qsub'

converter = Path('/home/users/kimjuneho4/foundation_mof/lammpterface/converter.py').expanduser()
python_path = '/home/users/kimjuneho4/anaconda3/envs/fmof/bin/python'

suffix = 'lammps-data'
NUM_QSUB = 1
NODE = 'ac'
#############################


def write_qsub(path_cif:Path, N:int, outdir=Path, NODE:str=NODE):   
    file = Path('/home/users/kimjuneho4/foundation_mof/qsub')/f'convert_{N}.qsub'
    cifid = path_cif.stem

    if not file.exists():
        with open(file, 'w') as f:
            f.write("#!/bin/sh\n")
            f.write("#PBS -r n\n")
            f.write("#PBS -q long\n")
            f.write(f"#PBS -l nodes=1:ppn=1:{NODE}\n")
            f.write("cd $PBS_O_WORKDIR\n\n")

    with open(file, 'a') as f:
        save_path = outdir/f'{cifid}.cif'
        f.write(f'{python_path} {converter} -i {str(path_cif.absolute())} -o {str(save_path.absolute())} > tmp_log_{N}.out 2>&1\n')
        f.write(f'echo {cifid} >> log_{N}.out\n')
        f.write(f'cat tmp_log_{N}.out >> log_{N}.out\n')


path = Path(path)
outdir = Path(outdir)

assert converter.exists(), str(converter)

if not path.exists():
    raise ValueError()

outdir.mkdir(exist_ok=True, parents=True)

list_cifs, len_cifs = tee(path.glob(f'*.{suffix}'))
len_cifs = sum([1 for _ in len_cifs])

n = len_cifs // NUM_QSUB

with open('./energy_new.txt', 'r') as f:
    lines = f.readlines()
    fail_stem = []

    for line in lines:
        stem = line.strip('\n')
        fail_stem.append(stem)

    for i, path_cif in tqdm(enumerate(list_cifs)):
        N = i // n
        write_qsub(path_cif, N, outdir)
