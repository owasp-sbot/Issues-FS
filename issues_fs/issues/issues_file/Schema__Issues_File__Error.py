# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Issues_File__Error - Parse error with source location
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe


class Schema__Issues_File__Error(Type_Safe):
    line_number : int                                                           # 1-based line number
    raw_line    : str                                                           # original line text
    message     : str                                                           # error description
