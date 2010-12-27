def PMTDetection(pmt_detect_length):
    """generate PMT detection event"""
    current_pm_counts = get_return_var("PM Count")
    if current_pm_counts == None:
        current_pm_counts = 0
    add_to_return_list("PM Count",current_pm_counts + 2)
    ttl_pulse("15",300, is_last=True)
