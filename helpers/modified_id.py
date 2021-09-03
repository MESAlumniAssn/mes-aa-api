def modify_record_id(record_id: int):
    return "0" + str(record_id) if record_id < 10 else record_id


def abbreviated_membership(membership_type: str):
    return "LM" if membership_type == "Lifetime" else "OM"
