import Rhino
import Grasshopper as gh
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import math


"""Use the base circle of the tube holder for calculating translation vector list"""
base_circle = rs.DuplicateEdgeCurves(tube_holder)[0]
center = rs.CircleCenterPoint(base_circle)
radius = rs.CircleRadius(base_circle)
unit_trans = 2 * radius
vertical_OD = [piezo_holder, tube_holder]
vec_list = []
permutation_circle = []
permutation_piezo_holder = []
permutation_tube_holder = []
scent_number = int(scent_number)


"""Generate the permutation of the base circle"""
def permutationCircle(vec_list):
    for vec in vec_list:
        copied_object = rs.CopyObject(base_circle, vec)
        permutation_circle.append(copied_object)
    return permutation_circle


"""Use convex hull to generate the bottom plate"""
def generatePedestal(permutation_circle, pcb_bottom_curve=None):
    convex_points = []
    segments = 1000
    for circle in permutation_circle:
        # division_points = rs.DivideCurve(circle, segments)
        convex_points.append(rs.DivideCurve(circle, segments))
    convex_points = [i for item in convex_points for i in item]
    
    if pcb_bottom_curve is not None:
        # divide the pcb_bottom_curve and append
        points = rs.DivideCurve(pcb_bottom_curve, segments)
        for point in points:
            convex_points.append(point)
    
    # get the pedestal polyline curve
    pedestal_polyline = ghcomp.ConvexHull(convex_points)[0]
    # create surface from the polyline curve
    pedestal_surface = rg.Brep.CreatePlanarBreps(pedestal_polyline)[0]
    pedestal_area = rg.Brep.GetArea(pedestal_surface)
    print(pedestal_area)
    return pedestal_surface, pedestal_area, pedestal_polyline


"""Change permutation according to selection, using 'Default Pattern' to optimize volume by default"""
if permutation_pattern is None: permutation_pattern = "Line Pattern"
if permutation_pattern == "Line Pattern":
    interval_trans = rs.CreateVector(interval, 0, 0)
    for i in range(scent_number):
        vec = i * rs.CreateVector(unit_trans, 0, 0) + i * interval_trans
        vec_list.append(vec)

elif permutation_pattern == "Rectangle Pattern":
    root = int(math.sqrt(scent_number))
    factor = int(scent_number / root)
    remainder =  int(scent_number - root*factor)
    unit_trans = unit_trans + interval
    for i in range(root):
        for j in range(factor):
            vec = rs.CreateVector(j*unit_trans, 0, 0) + rs.CreateVector(0, i*unit_trans, 0)
            vec_list.append(vec)
    for k in range(remainder):
        vec = rs.CreateVector((factor-1)*unit_trans + math.cos(30*math.pi/180)*unit_trans, unit_trans/2 + k*unit_trans, 0)
        vec_list.append(vec)

elif permutation_pattern == "Circle Pattern":
    unit_trans = unit_trans + interval
    if scent_number == 1:
        vec_0 = rs.CreateVector(0,0,0)
        vec_list.append(vec_0)
    else:
        construct_circle_radius = (radius + interval/2) / math.sin(math.pi / scent_number)
        construct_circle = rs.AddCircle(rs.CreatePoint(0,0,0), construct_circle_radius)
        division_points = rs.DivideCurve(construct_circle, scent_number)
        for point in division_points:
            vec_list.append(point - rs.CreatePoint(0,0,0))

elif permutation_pattern == "Centralized Pattern":
    unit_trans = unit_trans + interval
    vec_0 = rs.CreateVector(0,0,0)
    vec_list.append(vec_0)
    if scent_number != 1:
        # this pattern can only be used between 1~7
        pivot_point = rs.CreatePoint(unit_trans, 0 ,0)
        degrees = 360 / (scent_number-1)
        for i in range(scent_number-1):
            vec = rs.RotateObject(pivot_point, rs.CreatePoint(0, 0 ,0), i*degrees, None, copy=True)
            vec_list.append(vec)


"""Generate the permutation of multiple holders"""
for vec in vec_list:
    copied_object = rs.CopyObject(piezo_holder, vec)
    permutation_piezo_holder.append(copied_object)
    copied_object = rs.CopyObject(tube_holder, vec)
    permutation_tube_holder.append(copied_object)


"""Generate the pedestal of the scent_number when it is not single"""
permutation_circle = permutationCircle(vec_list)

"""Place the PCB case according to OD_PCB_integration"""
# the length of the PCB case is 33 (pre-informed)
pcb_length = 27
pcb_width = 31.2
smaller_distance_between_PCB_OD = 4
distance_between_PCB_OD = pcb_length / 2 + smaller_distance_between_PCB_OD

if scent_number == 1:
    # move the PCB case beside the tube holder and piezo holder
    distance = radius + distance_between_PCB_OD
    pcb_case_placement = rs.MoveObject(pcb_case, rs.CreateVector(distance*-1,0,0))
    
    if OD_PCB_integration:
        # use bounding box to extract the bottom edge
        pcb_bounding_box = rs.BoundingBox(pcb_case_placement)
        bottom_point = []
        # maximum_x = 0
        for point in pcb_bounding_box:
            point.Z = 0
            if point.Z == 0:
                bottom_point.append(point)
        #         if math.fabs(point.X) > maximum_x:
        #             maximum_x = point.X
        # for point in bottom_point:
        #     if point.X == maximum_x:
        #         point.X = point.X + 6
        
        # ensure closed polyline
        bottom_point.append(bottom_point[0])
        pcb_bottom_curve = rs.AddPolyline(bottom_point)
        pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle, pcb_bottom_curve)
        
        # move the pcb guide and union the pcb and pcb guide
        closet_point = rs.CreatePoint((radius+smaller_distance_between_PCB_OD)*-1,0,0)
        if pcb_guide_position == "back":
            pcb_guide = rs.RotateObject(pcb_guide, rs.CreatePoint(0, 0 ,0), 90, None, copy=True)
            trans = rs.CreatePoint(closet_point.X-pcb_length, closet_point.Y, closet_point.Z) - rs.CreatePoint(0,0,0)
            pcb_guide = rs.CopyObject(pcb_guide, trans)
            pcb_case_placement = rs.BooleanUnion([pcb_case_placement, pcb_guide])[0]
        elif pcb_guide_position == "side":
            pcb_guide = rs.RotateObject(pcb_guide, rs.CreatePoint(0, 0 ,0), 180, None, copy=True)
            trans = rs.CreatePoint(closet_point.X-pcb_length/2-2, closet_point.Y-pcb_width/2, closet_point.Z)
            pcb_guide = rs.CopyObject(pcb_guide, trans)
            pcb_case_placement = rs.BooleanUnion([pcb_case_placement, pcb_guide])[0]
    else:
        pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle)
        centroid = rs.SurfaceAreaCentroid(pedestal)[0]
        
        # add pcb_guide to OD directly
        if add_attachments_toOD:
            pcb_guide_onOD = rs.RotateObject(pcb_guide_onOD, rs.CreatePoint(0, 0 ,0), 90, None, copy=True)
            intersect_point = rs.CreatePoint(radius*-1, 0 ,0)
            print(intersect_point)
            OD_pcb_guide = rs.MoveObject(pcb_guide_onOD, rs.CreatePoint(intersect_point) - rs.CreatePoint(0,0,0))

            bottom_point = []
            bottom_point.append(rs.CreatePoint(intersect_point.X-3, intersect_point.Y+7, intersect_point.Z))
            bottom_point.append(rs.CreatePoint(intersect_point.X-3, intersect_point.Y-7, intersect_point.Z))
            
            # construct a line with the two vertices
            pcb_bottom_curve = rs.AddPolyline(bottom_point)
            pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle, pcb_bottom_curve)
            # move the pcb case again
            pcb_case_placement = rs.MoveObject(pcb_case, rs.CreateVector(distance*-1,0,0))
        
elif scent_number > 1:
    # calculate the number of pcb case used
    pcb_case_number = int(math.ceil(scent_number / 4))
    print(pcb_case_number, "pcb cases will be used")
    
    # PCB and OD can not be integrated when pcb_case_number > 1
    pcb_case_placement = []
    pcb_case_placement.append(rs.CopyObject(pcb_case, rs.CreateVector(-60,0,0)))
    if pcb_case_number > 1:
        OD_PCB_integration = False
        # pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle)
        for pcb in range(pcb_case_number-1):
            new_pcb_case = rs.CopyObject(pcb_case, rs.CreateVector(-60, (pcb_width+2)*(pcb+1), 0))
            pcb_case_placement.append(new_pcb_case)
    
    # generate pedestal for the OD and PCB case, and allow users to select which side to put the guide for attachments
    if OD_PCB_integration:
        OD_pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle)
        centroid = rs.SurfaceAreaCentroid(OD_pedestal)[0]
        
        if permutation_pattern == "Line Pattern" or permutation_pattern == "Rectangle Pattern":
            # rotate the pcb case
            pcb_case = rs.RotateObject(pcb_case, rs.CreatePoint(0, 0 ,0), -90, None, copy=True)
            
            line = rs.AddLine(centroid, rs.CreatePoint(centroid.X,centroid.Y+1000,centroid.Z))
            intersect_point = rs.CurveCurveIntersection(line, pedestal_polyline)[0][1]
            print(intersect_point)
            unit_trans = rs.CreateVector(0, 1*distance_between_PCB_OD, 0)
            new_pcb_point = rs.MoveObject(intersect_point, unit_trans)
            print(rs.CreatePoint(new_pcb_point))
            pcb_case_placement = rs.MoveObject(pcb_case, rs.CreatePoint(new_pcb_point) - rs.CreatePoint(0,0,0))
            
            # generate the pedestal
            if pcb_case_placement is not None:
                bottom_point = []    
                closet_point = rs.BrepClosestPoint(pcb_case_placement, centroid)[0]
                print(closet_point)
                bottom_point.append(rs.CreatePoint(closet_point.X-pcb_width/2, closet_point.Y, closet_point.Z))
                bottom_point.append(rs.CreatePoint(closet_point.X+pcb_width/2, closet_point.Y, closet_point.Z))
                
                # construct a line with the two vertices
                pcb_bottom_curve = rs.AddPolyline(bottom_point)
                pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle, pcb_bottom_curve)

            # move the pcb guide and union the pcb and pcb guide
            if pcb_guide_position == "back":
                trans = rs.CreatePoint(closet_point.X, closet_point.Y+pcb_length-1, closet_point.Z) - rs.CreatePoint(0,0,0)
                pcb_guide = rs.CopyObject(pcb_guide, trans)
                pcb_case_placement = rs.BooleanUnion([pcb_case_placement, pcb_guide])[0]
            elif pcb_guide_position == "side":
                pcb_guide = rs.RotateObject(pcb_guide, rs.CreatePoint(0, 0 ,0), 90, None, copy=True)
                trans = rs.CreatePoint(closet_point.X-pcb_width/2, closet_point.Y+pcb_length/2, closet_point.Z)
                pcb_guide = rs.CopyObject(pcb_guide, trans)
                pcb_case_placement = rs.BooleanUnion([pcb_case_placement, pcb_guide])[0]
                
        elif permutation_pattern == "Circle Pattern" or permutation_pattern == "Centralized Pattern":
            line = rs.AddLine(centroid, rs.CreatePoint(centroid.X-1000,centroid.Y,centroid.Z))
            intersect_point = rs.CurveCurveIntersection(line, pedestal_polyline)[0][1]
            print(intersect_point)
            unit_trans = rs.CreateVector(-1*distance_between_PCB_OD,0,0)
            new_pcb_point = rs.MoveObject(intersect_point, unit_trans)
            print(rs.CreatePoint(new_pcb_point))
            pcb_case_placement = rs.MoveObject(pcb_case, rs.CreatePoint(new_pcb_point) - rs.CreatePoint(0,0,0))
            
            # generate the pedestal
            if pcb_case_placement is not None:
                bottom_point = []
                closet_point = rs.BrepClosestPoint(pcb_case_placement, centroid)[0]
                print(closet_point)
                bottom_point.append(rs.CreatePoint(closet_point.X, closet_point.Y-pcb_width/2, closet_point.Z))
                bottom_point.append(rs.CreatePoint(closet_point.X, closet_point.Y+pcb_width/2, closet_point.Z))
                
                # construct a line with the two vertices
                pcb_bottom_curve = rs.AddPolyline(bottom_point)
                pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle, pcb_bottom_curve)
            
            # move the pcb guide and union the pcb and pcb guide
            if pcb_guide_position == "back":
                pcb_guide = rs.RotateObject(pcb_guide, rs.CreatePoint(0, 0 ,0), 90, None, copy=True)
                trans = rs.CreatePoint(closet_point.X-pcb_length+1, closet_point.Y, closet_point.Z) - rs.CreatePoint(0,0,0)
                pcb_guide = rs.CopyObject(pcb_guide, trans)
                pcb_case_placement = rs.BooleanUnion([pcb_case_placement, pcb_guide])[0]
            elif pcb_guide_position == "side":
                pcb_guide = rs.RotateObject(pcb_guide, rs.CreatePoint(0, 0 ,0), 180, None, copy=True)
                trans = rs.CreatePoint(closet_point.X-pcb_length/2-1, closet_point.Y-pcb_width/2, closet_point.Z)
                pcb_guide = rs.CopyObject(pcb_guide, trans)
                pcb_case_placement = rs.BooleanUnion([pcb_case_placement, pcb_guide])[0]
    
    # without OD_PCB_integration, users can add attachments to OD and PCB case respectively
    else:
        if add_attachments_toOD:
            pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle)
            centroid = rs.SurfaceAreaCentroid(pedestal)[0]
            
            if permutation_pattern == "Line Pattern" or permutation_pattern == "Rectangle Pattern":
                line = rs.AddLine(centroid, rs.CreatePoint(centroid.X,centroid.Y+1000,centroid.Z))
                intersect_point = rs.CurveCurveIntersection(line, pedestal_polyline)[0][1]
                print(intersect_point)
                OD_pcb_guide = rs.MoveObject(pcb_guide_onOD, rs.CreatePoint(intersect_point) - rs.CreatePoint(0,0,0))
                
                bottom_point = []
                bottom_point.append(rs.CreatePoint(intersect_point.X-7, intersect_point.Y+3, intersect_point.Z))
                bottom_point.append(rs.CreatePoint(intersect_point.X+7, intersect_point.Y+3, intersect_point.Z))

                # construct a line with the two vertices
                pcb_bottom_curve = rs.AddPolyline(bottom_point)
                pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle, pcb_bottom_curve)
            
            elif permutation_pattern == "Circle Pattern" or permutation_pattern == "Centralized Pattern":
                pcb_guide_onOD = rs.RotateObject(pcb_guide_onOD, rs.CreatePoint(0, 0 ,0), 90, None, copy=True)
                line = rs.AddLine(centroid, rs.CreatePoint(centroid.X-1000,centroid.Y,centroid.Z))
                intersect_point = rs.CurveCurveIntersection(line, pedestal_polyline)[0][1]
                print(intersect_point)
                OD_pcb_guide = rs.MoveObject(pcb_guide_onOD, rs.CreatePoint(intersect_point) - rs.CreatePoint(0,0,0))

                bottom_point = []
                bottom_point.append(rs.CreatePoint(intersect_point.X-3, intersect_point.Y+7, intersect_point.Z))
                bottom_point.append(rs.CreatePoint(intersect_point.X-3, intersect_point.Y-7, intersect_point.Z))
                
                # construct a line with the two vertices
                pcb_bottom_curve = rs.AddPolyline(bottom_point)
                pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle, pcb_bottom_curve)
        # users can also add no attachments to either OD or PCB
        else:
            pedestal, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle)
    
# if permutation_pattern == "Default Pattern":
    # unit_trans = unit_trans + interval
    # vec_0 = rs.CreateVector(0,0,0)
    # vec_list.append(vec_0)
    # point_list = []
    # point_list.append(center)

    # if scent_number >= 1:
    #     vec = rs.CreateVector(unit_trans, 0, 0)
    #     vec_list.append(vec)
    #     point_list.append(rs.CreatePoint(unit_trans, 0, 0))
        
    #     if scent_number > 2:
    #         # use hill climbing to minimize the bottom area
    #         tangent_vec = point_list[0] - point_list[1]
    #         center_point = (point_list[0] + point_list[1]) / 2
    #         unit_move = unit_trans * math.sin(60 * math.pi / 180)
    #         minimum_added_area = 100000
            
    #         for direction in range(2):
    #             # two normal vectors need to be considered
    #             if direction == 0:
    #                 up_vec = rs.CreateVector([0,0,1])
    #             elif direction == 1:
    #                 up_vec = rs.CreateVector([0,0,-1])
    #             normal = rs.VectorCrossProduct(up_vec, tangent_vec)
    #             normal = rs.VectorUnitize(normal)
    #             new_point = normal * unit_move + center_point
    #             new_vec = new_point - center
                
    #             vec_list.append(new_vec)
    #             permutation_circle = permutationCircle(vec_list)
    #             pedestal_surface, pedestal_area, pedestal_polyline = generatePedestal(permutation_circle)
    #             permutation_circle.pop()
    #             vec_list.pop()
                
    #             tuple_area = {new_vec, pedestal_area}
    #             # print(tuple_area)
