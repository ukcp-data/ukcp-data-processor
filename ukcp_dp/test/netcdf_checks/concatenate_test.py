"""
Take a list of NetCDF files from a file, load them into a cube and concatenate them.

"""
import sys

import iris
from iris.cube import CubeList
from iris.exceptions import ConcatenateError
from iris.util import equalise_attributes, unify_time_units


# point to a file containing the list of files to check
file_name = "ADD FULL FILE PATH HERE"


cubes_all = CubeList()

with open(file_name, "r") as file_list:
    for line in file_list:
        line = line.strip()
        print(f"Loading: {line}")
        cube = iris.load_cube(line)
        coords = cube.coords(var_name="creation_date")
        for coord in coords:
            cube.remove_coord(coord)
        cubes_all.append(cube)

equalise_attributes(cubes_all)
unify_time_units(cubes_all)

try:
    cubes_all.concatenate_cube()
except ConcatenateError as ex:
    print(ex)
    sys.exit(1)
    
print("Files concatenated into a cube")
