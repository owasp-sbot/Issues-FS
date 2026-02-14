# ═══════════════════════════════════════════════════════════════════════════════
# Parser__Issues_File - Parses a complete .issues file
# Handles indentation-based hierarchy, comments, blank lines
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from issues_fs.issues.issues_file.Parser__Issues_File__Line                     import Parser__Issues_File__Line
from issues_fs.issues.issues_file.Schema__Issues_File__Line                     import Schema__Issues_File__Line
from issues_fs.issues.issues_file.Schema__Issues_File__Error                    import Schema__Issues_File__Error
from issues_fs.issues.issues_file.Schema__Issues_File__Result                   import Schema__Issues_File__Result

SPACES_PER_INDENT = 4                                                          # 4 spaces = 1 indent level


class Parser__Issues_File(Type_Safe):
    line_parser : Parser__Issues_File__Line

    def parse(self, content: str, source_file: str = '') -> Schema__Issues_File__Result:
        issues : List[Schema__Issues_File__Line] = []
        errors : List[Schema__Issues_File__Error] = []
        parent_stack : List[str]                  = []                          # stack of labels at each indent level

        lines = content.split('\n')

        for line_number_0, raw_line in enumerate(lines):
            line_number = line_number_0 + 1                                     # 1-based line numbers

            if self.is_skip_line(raw_line):                                     # skip blank and comment lines
                continue

            indent_level       = self.measure_indent(raw_line)
            stripped_line      = raw_line.strip()
            parsed, error      = self.line_parser.parse(stripped_line, line_number)

            if error is not None:
                errors.append(error)
                continue

            parsed.indent_level = indent_level

            # maintain parent stack for hierarchy
            while len(parent_stack) > indent_level:                             # dedent: pop parents
                parent_stack.pop()

            if len(parent_stack) > 0:                                           # assign parent from stack
                parsed.parent_label = parent_stack[-1]

            # push this label onto stack at current level
            if len(parent_stack) == indent_level:                               # new level or same level
                parent_stack.append(parsed.label)
            else:
                parent_stack[indent_level] = parsed.label                       # replace at existing level

            issues.append(parsed)

        return Schema__Issues_File__Result(source_file = source_file ,
                                           issues      = issues      ,
                                           errors      = errors      )

    def is_skip_line(self, line: str) -> bool:                                  # blank or comment line
        stripped = line.strip()
        if stripped == '':
            return True
        if stripped.startswith('#'):
            return True
        return False

    def measure_indent(self, line: str) -> int:                                 # count indent level
        indent_chars = 0
        for char in line:
            if char == '\t':
                return self.count_tabs(line)                                    # tab mode
            elif char == ' ':
                indent_chars += 1
            else:
                break
        return indent_chars // SPACES_PER_INDENT                                # space mode

    def count_tabs(self, line: str) -> int:                                     # count leading tabs
        count = 0
        for char in line:
            if char == '\t':
                count += 1
            else:
                break
        return count
