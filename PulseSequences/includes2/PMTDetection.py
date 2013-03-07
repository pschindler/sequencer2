def PMTDetection(pmt_det_length):
    """generate PMT detection event"""

    current_pm_counts = get_return_var("PM Count")
    if current_pm_counts == None:
        current_pm_counts = 0
    add_to_return_list("PM Count", current_pm_counts + 2)
    ttl_pulse("PM_Gate", 100, start_time=0, is_last=False)
    ttl_pulse("PM_Gate", 100, start_time=pmt_det_length, is_last=True) 
