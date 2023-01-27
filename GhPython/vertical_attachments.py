from codecs import backslashreplace_errors
import Rhino
import Grasshopper as gh
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs

"""Let the user to choose whether the OD is angle adjustable"""
angle_adjustable = angle_adjustable
attchments_list = {'no_attachment': None,
                   'cylinder_clip': cylinder_clip,
                   'cubic_clip': cubic_clip,
                   'hair_clip_connector': hair_clip_connector,
                   'hook': hook,
                   'ring': ring,
                   'elastic': elastic,
                   'stand': stand,
                   'magnet': magnet,
                   'sticker': sticker}

PCB_attachment_methods = PCB_attachment_methods
print("PCB_attachment_methods:", PCB_attachment_methods)
OD_attachment_methods = OD_attachment_methods
print("OD_attachment_methods:", OD_attachment_methods)

# avoid outputting two identical objects
if PCB_attachment_methods is not None:
    pcb_gen_attchment = attchments_list[PCB_attachment_methods]
if pcb_gen_attchment is not None:
    if len(pcb_gen_attchment) == 2 and PCB_attachment_methods != 'ring' and PCB_attachment_methods != 'elastic':
        if rs.SurfaceVolume(pcb_gen_attchment[0]) == rs.SurfaceVolume(pcb_gen_attchment[1]):
            pcb_gen_attchment = pcb_gen_attchment[0]

if OD_attachment_methods is not None:
    od_gen_attchment = attchments_list[OD_attachment_methods]
if od_gen_attchment is not None:
    if len(od_gen_attchment) == 2 and OD_attachment_methods != 'ring' and OD_attachment_methods != 'elastic':
        if rs.SurfaceVolume(od_gen_attchment[0]) == rs.SurfaceVolume(od_gen_attchment[1]):
            od_gen_attchment = od_gen_attchment[0]


"""Users can select an attachment method to the PCB case"""
if pcb_gen_attchment is not None:
    if pcb_guide_position != 'no_guide' or pcb_guide_position is None:
        moved_distance = 60
        trans = rs.CreateVector(0,0,moved_distance)
        center_point = rs.CreatePoint(0,0,0)
        x_axis = rs.CreateVector(1,0,0)
        y_axis = rs.CreateVector(0,1,0)
        z_axis = rs.CreateVector(0,0,1)
        pcb_gen_attchment = rs.CopyObjects(pcb_gen_attchment, trans)

        if not OD_PCB_integration:
            pcb_guide_position = "back"
        
        if PCB_attachment_methods == 'stand':
            pcb_gen_attchment = rs.MoveObjects(pcb_gen_attchment, trans*-1)
            pcb_gen_attchment = rs.MoveObjects(pcb_gen_attchment, rs.CreateVector(moved_distance*-1,0,0))
        else:
            if pcb_guide_position == "back":
                pcb_gen_attchment = rs.RotateObjects(pcb_gen_attchment, center_point, 90, axis=z_axis, copy=False)
                pcb_gen_attchment = rs.RotateObjects(pcb_gen_attchment, center_point, -90, axis=x_axis, copy=False)
            elif pcb_guide_position == "side":
                pcb_gen_attchment = rs.RotateObjects(pcb_gen_attchment, center_point, -90, axis=y_axis, copy=False)
        
        if PCB_attachment_methods == 'ring' or PCB_attachment_methods == 'elastic':
            print("The Ring attachments can not be used with pcb_guide")
    else:
        if PCB_attachment_methods == 'ring' or PCB_attachment_methods == 'elastic':
            print("Only Ring and Elastic attachments can be used without pcb_guide")
            moved_distance = 60
            pcb_gen_attchment = rs.MoveObjects(pcb_gen_attchment, rs.CreateVector(moved_distance*-1,0,0))
        else:
            pcb_gen_attchment = None


"""Users can select attachments to OD and PCB case respectively"""
if OD_PCB_integration:
    od_gen_attchment = None
else:
    if pcb_gen_attchment is not None:
        # move pcb_gen_attchment to put it closer to the pcb case
        moved_distance = 60
        pcb_gen_attchment = rs.MoveObjects(pcb_gen_attchment, rs.CreateVector(moved_distance*-1,0,0))
    
    # generate attachments to OD when add_attachments_toOD is True
    if add_attachments_toOD:
        moved_distance = 60
        trans = rs.CreateVector(0,0,moved_distance)
        center_point = rs.CreatePoint(0,0,0)
        x_axis = rs.CreateVector(1,0,0)
        z_axis = rs.CreateVector(0,0,1)
        if OD_attachment_methods == 'stand':
            moved_distance = 60
            od_gen_attchment = rs.CopyObjects(od_gen_attchment, rs.CreateVector(0,moved_distance,0))
        else:
            od_gen_attchment = rs.CopyObjects(od_gen_attchment, trans)
            od_gen_attchment = rs.RotateObjects(od_gen_attchment, center_point, 90, axis=z_axis, copy=False)
            od_gen_attchment = rs.RotateObjects(od_gen_attchment, center_point, -90, axis=x_axis, copy=False)
            moved_distance = 20
            trans = rs.CreateVector(moved_distance,0,0)
            od_gen_attchment = rs.MoveObjects(od_gen_attchment, trans)
    # Ring and Elastic attachments can also be generated when add_attachments_toOD is False
    else:
        if OD_attachment_methods == 'ring' or OD_attachment_methods == 'elastic':
            print("Only Ring attachments can be used without pcb_guide")
            od_gen_attchment = rs.RotateObjects(od_gen_attchment, center_point, 90, axis=x_axis, copy=False)
            moved_distance = 60
            od_gen_attchment = rs.CopyObjects(od_gen_attchment, rs.CreateVector(moved_distance,0,0))
        else:
            od_gen_attchment = None