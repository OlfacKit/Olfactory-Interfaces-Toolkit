import Rhino
import Grasshopper as gh
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import math

scent_number = int(scent_number)
degrees = 360 / scent_number
if tube_holder_number is not None:
    count = int(tube_holder_number)

piezo_holder_list = []
tube_holder_list = []
tube_list = []
pedestal_list = []
limiters_list = []

if scent_number == 1:
    if tube_pattern_type == 'Straight Tubes':
        piezo_holder_list.append(objects_straight[0])
        tube_holder_list.append(objects_straight[1])
        for object in objects_straight[2:2+count]:
            tube_list.append(object)
        for object in objects_straight[2+count:2+count+count]:
            pedestal_list.append(object)
        for object in objects_straight[2+count+count:]:
            limiters_list.append(object)

    elif tube_pattern_type == 'Curved Tubes':
        piezo_holder_list.append(objects_curved[0])
        tube_holder_list.append(objects_curved[1])
        for object in objects_curved[2:2+count]:
            tube_list.append(object)
        for object in objects_curved[2+count:2+count+count]:
            pedestal_list.append(object)
        for object in objects_curved[2+count+count:]:
            limiters_list.append(object)

else:
    if permutation_pattern == 'Line Pattern':
        # line pattern can only use straight tubes
        tube_pattern_type = 'Straight Tubes'

    # list of objects for multi-scent display generation
    if tube_pattern_type == 'Straight Tubes':
        piezo_holder = objects_straight[0]
        tube_holder = objects_straight[1]
        straight_tube = objects_straight[2]
        straight_pedestal = objects_straight[3]
        limiters = objects_straight[4:]
        print("The number of limiters is", len(limiters))
           
        if permutation_pattern == "Circle Pattern":
            # rotate objects
            for num in range(scent_number):
                piezo_holder_list.append(rs.RotateObject(piezo_holder, pivot_center, num*degrees, None, copy=True))
                tube_holder_list.append(rs.RotateObject(tube_holder, pivot_center, num*degrees, None, copy=True))
                tube_list.append(rs.RotateObject(straight_tube, pivot_center, num*degrees, None, copy=True))
                if straight_pedestal is not None:
                    pedestal_list.append(rs.RotateObject(straight_pedestal, pivot_center, num*degrees, None, copy=True))
                if limiters is not None:
                    for limiter in limiters:
                        limiters_list.append(rs.RotateObject(limiter, pivot_center, num*degrees, None, copy=True))
        
        elif permutation_pattern == "Line Pattern":
            # copy objects and move
            for vec in line_pattern_vec_list:
                copied_object = rs.CopyObject(piezo_holder, vec)
                piezo_holder_list.append(copied_object)
                copied_object = rs.CopyObject(tube_holder, vec)
                tube_holder_list.append(copied_object)
                copied_object = rs.CopyObject(straight_tube, vec)
                tube_list.append(copied_object)
                if straight_pedestal is not None:
                    copied_object = rs.CopyObject(straight_pedestal, vec)
                    pedestal_list.append(copied_object)
                if limiters is not None:
                    for limiter in limiters:
                        copied_object = rs.CopyObject(limiter, vec)
                        limiters_list.append(copied_object)

    elif tube_pattern_type == 'Curved Tubes':
        piezo_holder = objects_curved[0]
        tube_holder = objects_curved[1]
        curved_tube = objects_curved[2]
        curved_pedestal = objects_curved[3]
        limiters = objects_curved[4:]
        
        # rotate objects
        for num in range(scent_number):
            piezo_holder_list.append(rs.RotateObject(piezo_holder, pivot_center, num*degrees, None, copy=True))
            tube_holder_list.append(rs.RotateObject(tube_holder, pivot_center, num*degrees, None, copy=True))
            tube_list.append(rs.RotateObject(curved_tube, pivot_center, num*degrees, None, copy=True))
            if curved_pedestal is not None:
                pedestal_list.append(rs.RotateObject(curved_pedestal, pivot_center, num*degrees, None, copy=True))
            if limiters is not None:
                for limiter in limiters:
                        limiters_list.append(rs.RotateObject(limiter, pivot_center, num*degrees, None, copy=True))