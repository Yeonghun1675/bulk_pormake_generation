"""
Molecular Simulation Laboratory
Last modified : 2021/08/26
Usage : python converter.py -i file_in -o file_out
Description : Code to convert btw simulation file formats
              possible inputs : .xyz, .cif, .cssr, .pdb, gaussian.com, gaussian.out, POSCAR, CONTCAR, OUTCAR, .lammps-data
              possible outputs : .xyz, .cif, .cssr, .pdb, gaussian.com, POSCAR, CONTCAR
Dependency : ase==3.20.0
             pymatgen==2022.0.8
Warning : Does not take connections in consider. Only the coordination infos.
"""
#################################################################
# Module Import
#################################################################
import sys

import argparse
from ase.build import make_supercell
from ase.io import read
from ase.data import atomic_masses, chemical_symbols
import numpy as np
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor


#################################################################
# Variables
#################################################################
parser = argparse.ArgumentParser(description="Code for converting atomic file format")
parser.add_argument("-i", "--FileIn", action='store', dest="FileIn", type=str, help="enter input filename")
parser.add_argument("-o", "--FileOut", action='store', dest="FileOut", type=str, help="enter output filename")
parser.add_argument("-c", action='store', help="enter cell info: 6 or 9 nums", nargs='*', type=float)
parser.add_argument("-e", action='store', help="make supercell: enter 3nums, if auto: expand according to cutoff 12.8", nargs='*')
args = parser.parse_args()


#################################################################
# class & func define
#################################################################
class Converter():
    must_pbc = ["cssr", "cif", "POSCAR", "CONTCAR"]
    wo_pbc = ["xyz", "com"]

    def __init__(self, args):
        # parse args
        self.file_in = args.FileIn
        self.file_out = args.FileOut
        self.in_type = self.file_in.split(".")[-1]
        self.out_type = self.file_out.split(".")[-1]

        if self.in_type == "cssr":
            self.atoms = AseAtomsAdaptor.get_atoms(Structure.from_file(self.file_in))
        else:
            self.atoms = read(self.file_in)
        self.cells = args.c
        self.expand = args.e
        self.check_cell()
        if self.expand:
            self.check_expand()
        if self.in_type == "lammps-data":
            for atom in self.atoms:
                min_value = min(atomic_masses, key=lambda k: abs(k-atom.mass))
                atom_num = atomic_masses.tolist().index(min_value)
                set_symbol = chemical_symbols[atom_num]
                atom.symbol = set_symbol

    def check_cell(self):
        # check if given cell params are appropriate and apply to atoms
        if self.cells:
            if len(self.cells) == 6:
                pass
            elif len(self.cells) == 9:
                self.cells = np.array(self.cells).reshape(3, 3)
            else:
                sys.exit("Error: Inappropriate number of input cell params given")
            self._apply_cell()

    def _apply_cell(self):
        self.atoms.set_pbc(True)
        self.atoms.set_cell(self.cells)

    def check_expand(self):
        # build supercell if expand option is given
        cells = self.atoms.get_cell()
        if cells:
            if self.expand[0] == "auto":
                P = np.diag(np.array(self._get_expanding_nums(cells)))
                print(P)
                self.atoms = make_supercell(self.atoms, P)
            elif len(self.expand) == 3:
                P = np.diag(np.array([int(x) for x in self.expand]))
                print(P)
                self.atoms = make_supercell(self.atoms, P)
            else:
                sys.exit("Wrong inputs for supercell")
        else:
            sys.exit("Expand only possible when cell exists")

    def _get_expanding_nums(self, cells, cutoff=12.8):
        # get expanding nums to expand cell over 2*cutoff
        vol = np.linalg.det(cells[:])
        a, b, c = cells[:]
        ha = vol / np.linalg.norm(np.cross(b, c))
        hb = vol / np.linalg.norm(np.cross(a, c))
        hc = vol / np.linalg.norm(np.cross(a, b))

        na = int(2*cutoff / ha) + 1
        nb = int(2*cutoff / hb) + 1
        nc = int(2*cutoff / hc) + 1
        return na, nb, nc

    def convert(self):
        if self.out_type in Converter.must_pbc and not np.any(self.atoms.get_pbc()):
            sys.exit("Cell params are essential in the case")

        if self.out_type == "cssr":
            self.structure = AseAtomsAdaptor.get_structure(self.atoms)
            self.structure.to(filename=self.file_out)
        else:
            self.convert_ase()

    def convert_ase(self):
        if self.out_type in Converter.wo_pbc:
            self.atoms.set_pbc(False)
        if self.out_type in ["POSCAR", "CONTCAR"]:
            self.atoms.write(
                self.file_out,
                direct=True,
                sort=True,
                long_format=False,
                vasp5=True
            )
        else:
            self.atoms.write(self.file_out)
        self._modify_xyz()

    def _modify_xyz(self):
        if self.out_type == "xyz":
            with open(self.file_out, 'r') as f:
                data = f.readlines()
                head = data[0]
                body = [line.split()[:4] for line in data[2:]]
                body = ["\n" + "\t".join(line) for line in body]

            with open(self.file_out, 'w') as fw:
                fw.write(head)
                for line in body:
                    fw.write(line)


#################################################################
# Main Code Line
#################################################################
def main():
    converter = Converter(args)
    converter.convert()


if __name__ == "__main__":
    main()

# End of Code
# K̲A̲I̲S̲T̲ M̲O̲L̲S̲I̲M̲
