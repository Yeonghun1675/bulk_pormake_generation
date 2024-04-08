import sys
from pathlib import Path
from tqdm import tqdm
from copy import deepcopy


def iter_len(iters):
	copy_iters = deepcopy(iters)
	return sum([1 for _ in copy_iters])


def mol_to_xyz(mol_file:Path, outdir:Path, connection_atom='F'):
    bb_name = mol_file.stem

    with open(mol_file, "r") as f:
        lines = f.readlines()
        f.close()
    
    # line coords and bonds from mol file
    line = lines[3].split()
    
    if len(line[0]) <= 3:
        num_atoms = int(line[0])
        num_bonds = int(line[1])
    else:
        num_atoms = int(line[0][:3])
        num_bonds = int(line[0][3:])

    # write xyz files
    outdir.mkdir(exist_ok=True, parents=True)
	
    with open(outdir/f"{bb_name}.xyz", "w") as f:
        f.write(f"{num_atoms}\n")
        f.write(f"mol to xyz file\n")
        # coords
        for line in lines[4:4+num_atoms]:
            tokens = line.split()
            # change dummy atoms R to X
            if tokens[3] == connection_atom:
                tokens[3] = "X"
            f.write(f"{tokens[3]:<10}    {tokens[0]:<10}    {tokens[1]:<10}    {tokens[2]:<10}\n")
        # bonds
        for line in lines[4+num_atoms:4+num_atoms+num_bonds]:
            tokens = [int(line[:3]), int(line[3:6]), int(line[6:9])]
            # bond type
            if tokens[2] == 1:
                bond_type = "S"
            elif tokens[2] == 2:
                bond_type = "D"
            elif tokens[2] == 3:
                bond_type = "T"
            elif tokens[2] == 4:
                bond_type = "A"
            else:
                raise Exception("bond type error")
            # find index of atom
            idx_1 = int(tokens[0]) - 1
            idx_2 = int(tokens[1]) - 1
            f.write(f"{idx_1:<10}{idx_2:<6}{bond_type:<6}\n")
        f.close()


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 3:
        raise ValueError(f'argv must be 3, not {len(argv)}')
    
    indir = Path(argv[1])
    outdir = Path(argv[2])
    
    assert indir.exists()
    
    if indir.is_dir():
        for file in indir.glob('*.mol'):
            try:
                mol_to_xyz(file, outdir)
            except Exception as e:
                print (file)
                print (e)
                sys.exit()
    else:
        file = indir
        mol_to_xyz(file, outdir)

