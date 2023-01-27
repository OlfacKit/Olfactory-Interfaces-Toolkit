import Rhino.Geometry as rg
import rhinoscriptsyntax as rs

scent_number = int(scent_number)
if tube_holder_number == None: tube_holder_number = 1
tube_holder_number = int(tube_holder_number)

if scent_number > 1:
    print("The tube holder number is re-adjusted to 1!")
    tube_holder_number = 1
else:
    tube_holder_number = tube_holder_number
