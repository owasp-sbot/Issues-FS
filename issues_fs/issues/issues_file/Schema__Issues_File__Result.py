# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Issues_File__Result - Container for parse results from a .issues file
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from issues_fs.issues.issues_file.Schema__Issues_File__Line                     import Schema__Issues_File__Line
from issues_fs.issues.issues_file.Schema__Issues_File__Error                    import Schema__Issues_File__Error


class Schema__Issues_File__Result(Type_Safe):
    source_file : str                                                           # which .issues file this came from
    issues      : List[Schema__Issues_File__Line]                               # successfully parsed lines
    errors      : List[Schema__Issues_File__Error]                              # parse errors collected
