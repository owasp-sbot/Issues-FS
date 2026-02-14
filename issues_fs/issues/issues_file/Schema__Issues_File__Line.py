# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Issues_File__Line - Intermediate representation of a parsed .issues line
# Holds the raw parsed data before conversion to Schema__Node
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe

# todo: all these vars and collections need to be type safe
class Schema__Issues_File__Line(Type_Safe):
    label        : str                                                          # raw label e.g. "Task-1"
    status       : str                                                          # raw status e.g. "todo"
    description  : str                                                          # raw description text
    indent_level : int                                                          # 0 = top-level, 1 = child, etc.
    parent_label : str                                                          # label of parent from indentation
    cross_refs   : List[str]                                                    # labels referenced via -> syntax
    line_number  : int                                                          # source line for error reporting
    issue_type   : str                                                          # inferred type e.g. "task", "bug"
