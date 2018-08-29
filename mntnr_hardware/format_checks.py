from jsonschema import draft4_format_checker

from mntnr_hardware.models import CabinetAttachmentEnum, CabinetFastenerEnum


@draft4_format_checker.checks('cabinet_attachment_enum')
def validate_cabinet_attachment_enum(value):
    if value in CabinetAttachmentEnum.__members__.keys():
        return True
    return False


@draft4_format_checker.checks('cabinet_fastener_enum')
def validate_cabinet_fastener_enum(value):
    if value in CabinetFastenerEnum.__members__.keys():
        return True
    return False
