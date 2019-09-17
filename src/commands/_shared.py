from src.packages.utils.ratlib import try_parse_uuid


def coerce_rescue_type(target):
    if target.isnumeric():
        target = int(target)
    else:
        target_mabie = try_parse_uuid(target)

        if target_mabie:
            target = target_mabie

        del target_mabie
    return target