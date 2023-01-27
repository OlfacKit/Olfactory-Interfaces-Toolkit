# Users selects the vertical scent container
if is_vertical_od:
    print("Show vertical parts")
    # preview off horizontal od
    hor_piezo_holder_list = None
    hor_tube_holder_list = None
    hor_tube_list = None
    hor_pedestal_list = None
    hor_limiters_list = None
    magnets_on_od = None
    pcb_case_with_magnets = None
    pcb_case_without_magnets = None
    hor_pcb_attchment = None
    hor_od_attchment = None
    hor_multiscent_pedestal = None

# Users selects the horizontal scent container
else:
    print("Show horizontal parts")
    # preview off vertical od
    vertical_piezo_holder = None
    vertical_tube_holder = None
    vertical_pedestal_and_pcb_case = None
    vertical_pcb_attchment = None
    vertical_od_attchment = None
