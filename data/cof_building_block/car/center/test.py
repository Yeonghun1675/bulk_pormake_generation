import ase.io

file = 'C1.car'
atoms = ase.io.read(file)
print (atoms)

ase.io.write('C1.mol', atoms)
