def PMTDetection(pmt_detect_length):
    """generate PMT detection event"""
    add_to_return_list("PM Count",2)
    ttl_pulse("15",300, is_last=True)
