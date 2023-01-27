import Rhino
import Grasshopper as gh
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import math


scent_number = int(scent_number)
if tube_holder_number == None: tube_holder_number = 1
tube_holder_number = int(tube_holder_number)


def detectTubeIntersection(arc_start_point, radius_of_curvature, tube_holder_number, scent_number, pivot_center):
    # get the original circle
    arc_start_point = rs.coerce3dpoint(arc_start_point)
    center_point_x = arc_start_point.X
    center_point_y = arc_start_point.Y - radius_of_curvature
    center_point_z = arc_start_point.Z
    center_point = rs.CreatePoint(center_point_x, center_point_y, center_point_z)
    pivot_circle = rs.AddCircle(center_point, math.fabs(radius_of_curvature))
    
    # get the first rotated circle to calculate intersection points
    if scent_number == 1:
        rotation_angle = 360 / tube_holder_number
        if radius_of_curvature > 0:
            rotation_angle = rotation_angle * -1
        rotated_circle = rs.RotateObject(pivot_circle, (0,0,0), rotation_angle, None, True)
        rotated_center_point = rs.CircleCenterPoint(rotated_circle, segment_index=-1, return_plane=False)
    else:
        rotation_angle = 360 / scent_number
        if radius_of_curvature > 0:
            rotation_angle = rotation_angle * -1
        rotated_circle = rs.RotateObject(pivot_circle, pivot_center, rotation_angle, None, True)
        rotated_center_point = rs.CircleCenterPoint(rotated_circle, segment_index=-1, return_plane=False)
    
    # get intersection points
    intersection_list = rs.CurveCurveIntersection(pivot_circle, rotated_circle)
    intersection_points = []
    if intersection_list is None:
        # print("Selected curves do not intersect")
        return intersection_points
    for intersection in intersection_list:
        if intersection[0] == 1:
            intersection_points.append(intersection[1])
    return intersection_points
    

def calculateArcEndPoint(customized_tube_length, tube_holder_number, radius_of_curvature, arc_start_point, arc_direction, pivot_center):
    arc_radian = customized_tube_length / radius_of_curvature
    arc_start_point = rs.coerce3dpoint(arc_start_point)
    end_point_x = arc_start_point.X + radius_of_curvature * math.sin(arc_radian)
    end_point_y = arc_start_point.Y - radius_of_curvature + radius_of_curvature * math.cos(arc_radian)
    end_point_z = arc_start_point.Z
    arc_end_point = rs.CreatePoint(end_point_x, end_point_y, end_point_z)
    
    # detect intersection of curved tubes to avoid collision
    intersection_points = detectTubeIntersection(arc_start_point, radius_of_curvature, tube_holder_number, scent_number, pivot_center)
    print(intersection_points)
    
    if intersection_points is None and tube_holder_number == 2:
        if arc_radian >= 310 * math.pi / 180:
            if radius_of_curvature > 0:
                radius_of_curvature += 0.1
            else:
                radius_of_curvature -= 0.1
            arc_end_point, radius_of_curvature, intersection_points = calculateArcEndPoint(customized_tube_length, tube_holder_number, radius_of_curvature, arc_start_point, arc_direction, pivot_center)
    # tube_holder_number = 3
    elif intersection_points is None and tube_holder_number == 3:
        if arc_radian >= 260 * math.pi / 180:
            if radius_of_curvature > 0:
                radius_of_curvature += 0.1
            else:
                radius_of_curvature -= 0.1
            arc_end_point, radius_of_curvature, intersection_points = calculateArcEndPoint(customized_tube_length, tube_holder_number, radius_of_curvature, arc_start_point, arc_direction, pivot_center)
    # tube_holder_number = 1,2, or scent_number == 2,3
    elif len(intersection_points) == 0 or len(intersection_points) == 1:
        if arc_radian >= 310 * math.pi / 180:
            if radius_of_curvature > 0:
                radius_of_curvature += 0.1
            else:
                radius_of_curvature -= 0.1
            arc_end_point, radius_of_curvature, intersection_points = calculateArcEndPoint(customized_tube_length, tube_holder_number, radius_of_curvature, arc_start_point, arc_direction, pivot_center)
        
        if scent_number == 3:
            if arc_radian >= 280 * math.pi / 180:
                if radius_of_curvature > 0:
                    radius_of_curvature += 0.1
                else:
                    radius_of_curvature -= 0.1
                arc_end_point, radius_of_curvature, intersection_points = calculateArcEndPoint(customized_tube_length, tube_holder_number, radius_of_curvature, arc_start_point, arc_direction, pivot_center)

        if scent_number == 4:
            if arc_radian >= 240 * math.pi / 180:
                if radius_of_curvature > 0:
                    radius_of_curvature += 0.1
                else:
                    radius_of_curvature -= 0.1
                arc_end_point, radius_of_curvature, intersection_points = calculateArcEndPoint(customized_tube_length, tube_holder_number, radius_of_curvature, arc_start_point, arc_direction, pivot_center)

    # tube_holder_number = 4 to 8
    else:
        # get the smallest distance between the arc end point and intersection points
        distance = 1000
        for point in intersection_points:
            dist = rs.Distance(arc_end_point, point)
            if dist < distance:
                distance = dist
        print("Distance:", distance)
        
        # find the smallest arc with intersection points
        arc1 = rs.AddArcPtTanPt(arc_start_point, arc_direction, intersection_points[0])
        arc1_radian = rs.ArcAngle(arc1) * math.pi / 180
        arc2 = rs.AddArcPtTanPt(arc_start_point, arc_direction, intersection_points[1])
        arc2_radian = rs.ArcAngle(arc2) * math.pi / 180
        smaller_radian = arc1_radian
        if smaller_radian > arc2_radian:
            smaller_radian = arc2_radian
        
        # update the radius of curvature by distance and re-calculate the arc end point
        if distance <= 10 or math.fabs(arc_radian) >= smaller_radian:
            if radius_of_curvature > 0:
                radius_of_curvature += 0.1
            else:
                radius_of_curvature -= 0.1
            arc_end_point, radius_of_curvature, intersection_points = calculateArcEndPoint(customized_tube_length, tube_holder_number, radius_of_curvature, arc_start_point, arc_direction, pivot_center)
        else:
            pass
    return arc_end_point, radius_of_curvature, intersection_points


def generatePedestalforCurvedTubes(pivot_arc, limiter_radius, gen_limiters, inner_tube_length):
    # offset pivot_arc and project it to the XY plane
    inward_curve = rs.OffsetCurve(pivot_arc, [0,0,0], limiter_radius*-1)[0]
    inward_curve = rg.Curve.ProjectToPlane(rs.coercecurve(inward_curve), rs.WorldXYPlane())
    outward_curve = rs.OffsetCurve(pivot_arc, [0,0,0], limiter_radius)[0]
    outward_curve = rg.Curve.ProjectToPlane(rs.coercecurve(outward_curve), rs.WorldXYPlane())
    
    line1 = rs.AddLine(rs.CurveStartPoint(inward_curve), rs.CurveStartPoint(outward_curve))
    line2 = rs.AddLine(rs.CurveEndPoint(outward_curve), rs.CurveEndPoint(inward_curve))
    joined_srf = rs.AddEdgeSrf([line1, outward_curve, line2, inward_curve])
    
    last_limiter = gen_limiters[0]
    cutter_srf = rs.ExtractSurface(last_limiter, 0, copy=True)[0]
    splited_srf_list = rs.SplitBrep(joined_srf, cutter_srf, delete_input=False)
    print("The number of splited surfaces:", len(splited_srf_list))
    
    largest_area = 0
    print(splited_srf_list)
    for face in splited_srf_list:
        area = rs.SurfaceArea(face)[0]
        if area > largest_area:
            largest_area = area
            largest_srf = face
    pedestal_srf = rs.JoinSurfaces([largest_srf, cutter_srf], delete_input=False)
    # pedestal_srf = rs.coercebrep(pedestal_srf, True)
    # pedestal_part = ghcomp.Extrude(pedestal_srf, rs.CreatePoint(0,0,1.5) - rs.CreatePoint(0,0,0))
    # rec_face = rs.ExtractSurface(pedestal_part, 3, copy=True)[0]
    # rec_face = rs.coercebrep(rec_face, True)
    # pedestal_rec = ghcomp.Extrude(rec_face, rs.CreatePoint(inner_tube_length*-1,0,0) - rs.CreatePoint(0,0,0))
    # pedestal = rs.BooleanUnion([pedestal_part, pedestal_rec], delete_input=False)[0]
    return pedestal_srf
    

def generatePedestalforStraightTubes(gen_limiters):
    # use convex hull to generate the pedestal for straight tubes
    convex_points = []
    segments = 500
    last_limiter = gen_limiters[0]
    last_limiter_curve = rs.DuplicateEdgeCurves(last_limiter)[0]
    convex_points.append(rs.DivideCurve(last_limiter_curve, segments))
    
    translate = rs.CreatePoint(0,0,0) - rs.CircleCenterPoint(last_limiter_curve, segment_index=-1, return_plane=False)
    copy_last_limiter_curve = rs.CopyObject(last_limiter_curve, translate)
    convex_points.append(rs.DivideCurve(copy_last_limiter_curve, segments))
    convex_points = [i for item in convex_points for i in item]
    
    pedestal_polyline = ghcomp.ConvexHull(convex_points)[0]
    pedestal_surface = rg.Brep.CreatePlanarBreps(pedestal_polyline)[0]
    return pedestal_surface


"""
Users select the number of scents
"""
if scent_number == 1:
    tube_holder_number = tube_holder_number
    # pivot_center = rs.CreatePoint(0,0,0)
    
    if OD_PCB_integration:
        # place the PCB case and move magnets for solid difference
        if tube_holder_number % 2 == 0:
            magnets_placement_point = rs.CreatePoint(0,0,0)
            magnets_rotation_angle = math.radians(360)
        elif tube_holder_number % 2 == 1:
            magnet_radius = magnet_radius
            magnets_placement_point = rs.CreatePoint(magnet_radius,0,0)
            magnets_rotation_angle = math.radians(360)
    else:
        pcb_case_preview = pcb_case_without_magnets

elif scent_number > 1:
    tube_holder_number = 1
    print("The tube holder number is re-adjusted to 1!")
    
    # extract the bottom circle edge of the tube holder
    tube_holder = rs.coercebrep(tube_holder)
    tube_holder_edges = rg.Brep.DuplicateEdgeCurves(tube_holder)
    for edge in tube_holder_edges:
        edge = rs.coercecurve(edge)
        if rs.IsCircle(edge):
            if rs.CircleCenterPoint(edge) == rs.CreatePoint(0,0,0):
                base_circle = edge
    
    center = rs.CircleCenterPoint(base_circle)
    radius = rs.CircleRadius(base_circle)
    print("Radius of the base circle", radius) 
    
    if permutation_pattern == "Circle Pattern":
        # get the pivot point for populate rotated objects
        construct_circle_radius = (radius + interval / 2) / math.sin(math.pi / scent_number)
        translate = rs.CreateVector(construct_circle_radius*-1, 0, 0)
        pivot_center = rs.CopyObject(center, translate)
        print("The pivot_center point is", rs.coerce3dpoint(pivot_center))
        # pivot_center_base_circle_param = rs.CurveClosestPoint(base_circle, pivot_center)
        # pivot_center_base_circle_point = rs.EvaluateCurve(base_circle, pivot_center_base_circle_param)
        # pivot_center_base_circle_distance = rs.Distance(pivot_center, pivot_center_base_circle_point)
        
        # use convex hull to generate the inner pedestal
        degrees = 360 / scent_number
        convex_points = []
        segments = 500
        for num in range(scent_number):
            pivot_circle = rs.RotateObject(base_circle, pivot_center, num*degrees, None, copy=True)
            convex_points.append(rs.DivideCurve(pivot_circle, segments))
        convex_points = [i for item in convex_points for i in item]
        inner_pedestal_polyline = ghcomp.ConvexHull(convex_points)[0]
        inner_pedestal_surface = rg.Brep.CreatePlanarBreps(inner_pedestal_polyline)[0]
        
        # extrude the surface to a brep as the inner pedestal
        extrude_curve = rs.AddLine(pivot_center, rs.CopyObject(pivot_center, rs.CreateVector(0,0,pedestal_height)))
        inner_pedestal = rs.ExtrudeSurface(inner_pedestal_surface, extrude_curve, cap=True)
        
        # place the PCB case and move magnets for solid difference only when the OD and PCB case are integrated
        if OD_PCB_integration:
            magnets_placement_point = pivot_center
            if scent_number == 2:
                magnets_rotation_angle = math.radians(360)
            else:
                magnets_rotation_angle = math.radians(180 / scent_number)
        else:
            pcb_case_preview = pcb_case_without_magnets
        
    elif permutation_pattern == "Line Pattern":
        unit_trans = 2 * radius
        interval_trans = rs.CreateVector(0, interval, 0)
        line_pattern_vec_list = []
        convex_points = []
        segments = 500
        for i in range(scent_number):
            vec = i * rs.CreateVector(0, unit_trans, 0) + i * interval_trans
            line_pattern_vec_list.append(vec)
            copied_circle = rs.CopyObject(base_circle, vec)
            convex_points.append(rs.DivideCurve(copied_circle, segments))
        convex_points = [i for item in convex_points for i in item]
        inner_pedestal_polyline = ghcomp.ConvexHull(convex_points)[0]
        inner_pedestal_surface = rg.Brep.CreatePlanarBreps(inner_pedestal_polyline)[0]
        
        # extrude the surface to a brep as the inner pedestal
        extrude_curve = rs.AddLine(center, rs.CopyObject(center, rs.CreateVector(0,0,pedestal_height)))
        inner_pedestal = rs.ExtrudeSurface(inner_pedestal_surface, extrude_curve, cap=True)
    
        # line pattern can only use straight tubes
        tube_pattern_type = 'Straight Tubes'
        
        # place the PCB case and move magnets for solid difference
        if OD_PCB_integration:
            magnets_placement_point = rs.SurfaceAreaCentroid(inner_pedestal_surface)[0]
            magnets_rotation_angle = math.radians(90)
        else:
            pcb_case_preview = pcb_case_without_magnets

"""
Users select the type of tube pattern
"""
if tube_pattern_type == 'Straight Tubes':
    straight_tube_length = customized_tube_length
    curved_tube_length = 0
    print(tube_pattern_type, straight_tube_length)
    
    # generate limiters according to the tube length
    plug_length = 15
    gen_limiters = []
    interval = customized_tube_length - plug_length
    if interval >= 30:
        translate = rs.CreatePoint(interval+inner_tube_length,0,0) - rs.CreatePoint(0,0,0)
        gen_limiters.append(rs.CopyObject(limiter, translate))
    if interval >= 60:
        translate = rs.CreatePoint(interval/2+inner_tube_length,0,0) - rs.CreatePoint(0,0,0)
        gen_limiters.append(rs.CopyObject(limiter, translate))
    
    if len(gen_limiters) != 0:
        pedestal_srf_straight_tube = generatePedestalforStraightTubes(gen_limiters)
        
elif tube_pattern_type == 'Curved Tubes':
    curved_tube_length = customized_tube_length
    straight_tube_length = 0
    print(tube_pattern_type, curved_tube_length)
    
    # constrain the radius of curvature based on tube's ability to bend 
    if minimum_radius_of_curvature * -1 < radius_of_curvature < 0:
        radius_of_curvature = minimum_radius_of_curvature * -1
    elif 0 <= radius_of_curvature < minimum_radius_of_curvature:
        radius_of_curvature = minimum_radius_of_curvature
      
    # calculate the arc end point to construct the arc for creating PTFE tube pipe geometry
    arc_end_point, radius_of_curvature, intersection_points = calculateArcEndPoint(customized_tube_length, tube_holder_number, radius_of_curvature, arc_start_point, arc_direction, pivot_center)
    print("Radius of curvature", radius_of_curvature)
    
    # generate limiters according to the tube length
    plug_length = 16
    gen_limiters = []
    interval = customized_tube_length - plug_length
    pivot_arc = rs.AddArcPtTanPt(arc_start_point, arc_direction, arc_end_point)
    count = rs.ArcAngle(pivot_arc) // 90
    if interval >= 20:
        if count == 0:
            end_point = rs.CurveArcLengthPoint(pivot_arc, interval, from_start=True)
            translate = rs.CreatePoint(end_point.X, end_point.Y, 0) - rs.CreatePoint(0,0,0)
            gen_limiters.append(rs.CopyObject(limiter, translate))
        else:
            interval = interval / count
            for i in range(int(count)):
                i = count - i
                end_point = rs.CurveArcLengthPoint(pivot_arc, interval*i, from_start=True)
                translate = rs.CreatePoint(end_point.X, end_point.Y, 0) - rs.CreatePoint(0,0,0)
                gen_limiters.append(rs.CopyObject(limiter, translate))
    
    # generate the pedestal only if limiters are used
    if len(gen_limiters) != 0:
        pedestal_srf_curved_tube = generatePedestalforCurvedTubes(pivot_arc, limiter_radius, gen_limiters, inner_tube_length)
        
# inform users the required tube length
required_tube_length = inner_tube_length + customized_tube_length
print("Required tube length:", required_tube_length)