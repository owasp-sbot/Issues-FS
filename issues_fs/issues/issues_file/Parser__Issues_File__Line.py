# ═══════════════════════════════════════════════════════════════════════════════
# Parser__Issues_File__Line - Parses a single line from a .issues file
# Extracts label, status, description, cross-references, and inferred type
# ═══════════════════════════════════════════════════════════════════════════════

import re
from typing                                                                     import Optional, Tuple
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from issues_fs.issues.issues_file.Schema__Issues_File__Line                     import Schema__Issues_File__Line
from issues_fs.issues.issues_file.Schema__Issues_File__Error                    import Schema__Issues_File__Error

CROSS_REF_PATTERN = re.compile(r'->\s*([A-Z][a-zA-Z]*(?:-[A-Z][a-zA-Z]*)*-\d{1,5})')
LABEL_TYPE_PATTERN = re.compile(r'^(.+)-\d{1,5}$')


class Parser__Issues_File__Line(Type_Safe):

    def parse(self, line: str, line_number: int = 0) -> Tuple[Optional[Schema__Issues_File__Line],
                                                               Optional[Schema__Issues_File__Error]]:
        parts = line.split('|', 2)                                              # split on first two pipes only

        if len(parts) < 3:
            error = Schema__Issues_File__Error(line_number = line_number    ,
                                               raw_line    = line           ,
                                               message     = 'Expected format: label | status | description')
            return (None, error)

        label       = parts[0].strip()
        status      = parts[1].strip()
        description = parts[2].strip()

        if not label:
            error = Schema__Issues_File__Error(line_number = line_number ,
                                               raw_line    = line        ,
                                               message     = 'Label is empty')
            return (None, error)

        if not status:
            error = Schema__Issues_File__Error(line_number = line_number ,
                                               raw_line    = line        ,
                                               message     = 'Status is empty')
            return (None, error)

        cross_refs = CROSS_REF_PATTERN.findall(description)                     # extract -> TargetLabel references
        issue_type = self.infer_type_from_label(label)

        parsed = Schema__Issues_File__Line(label        = label        ,
                                           status       = status       ,
                                           description  = description  ,
                                           indent_level = 0            ,        # set by file parser
                                           parent_label = ''           ,        # set by file parser
                                           cross_refs   = cross_refs   ,
                                           line_number  = line_number  ,
                                           issue_type   = issue_type   )
        return (parsed, None)

    def infer_type_from_label(self, label: str) -> str:                         # Extract type from label prefix
        match = LABEL_TYPE_PATTERN.match(label)                                 # e.g. "Task-1" -> "Task"
        if match:
            type_prefix = match.group(1)                                        # e.g. "Task", "User-Journey"
            return type_prefix.lower()                                          # e.g. "task", "user-journey"
        return ''
