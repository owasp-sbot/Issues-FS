# ═══════════════════════════════════════════════════════════════════════════════
# Issues_File__Check__Service - Validates .issues files and reports problems
# Implements the `issues-fs check` logic: parse, validate, summarise
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Dict, List, Set
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from issues_fs.issues.issues_file.Issues_File__Loader__Service                  import Issues_File__Loader__Service
from issues_fs.issues.issues_file.Issues_File__Loader__Service                  import Schema__Issues_File__Load__Result
from issues_fs.issues.issues_file.Schema__Issues_File__Error                    import Schema__Issues_File__Error


class Schema__Issues_File__Check__Summary(Type_Safe):
    total_issues     : int
    total_errors     : int
    issues_by_type   : dict                                                     # {type_name: count}
    issues_by_status : dict                                                     # {status: count}
    files_checked    : List[str]
    duplicate_labels : List[str]                                                # labels that appear more than once
    broken_refs      : List[str]                                                # cross-refs pointing to non-existent labels
    mixed_indent     : List[str]                                                # files mixing tabs and spaces
    is_valid         : bool                                                     # True if no errors, no duplicates, no broken refs


class Issues_File__Check__Service(Type_Safe):
    loader : Issues_File__Loader__Service

    def check_content(self, content: str, source_file: str = ''
                     ) -> Schema__Issues_File__Check__Summary:
        return self.check_multiple([(content, source_file)])

    def check_multiple(self, files: List[tuple]
                      ) -> Schema__Issues_File__Check__Summary:
        load_result = self.loader.load_multiple(files)

        duplicate_labels = self.find_duplicate_labels(load_result)
        broken_refs      = self.find_broken_refs(files)
        mixed_indent     = self.find_mixed_indent(files)

        issues_by_type   = {}
        issues_by_status = {}
        for node in load_result.nodes:
            t = str(node.node_type)
            s = str(node.status)
            issues_by_type[t]   = issues_by_type.get(t, 0) + 1
            issues_by_status[s] = issues_by_status.get(s, 0) + 1

        all_errors = list(load_result.errors)
        is_valid   = (len(all_errors) == 0 and
                      len(duplicate_labels) == 0 and
                      len(broken_refs) == 0)

        return Schema__Issues_File__Check__Summary(
            total_issues     = load_result.total_issues                          ,
            total_errors     = len(all_errors)                                   ,
            issues_by_type   = issues_by_type                                    ,
            issues_by_status = issues_by_status                                  ,
            files_checked    = load_result.files_loaded                           ,
            duplicate_labels = duplicate_labels                                   ,
            broken_refs      = broken_refs                                        ,
            mixed_indent     = mixed_indent                                       ,
            is_valid         = is_valid                                           )

    def find_duplicate_labels(self, load_result: Schema__Issues_File__Load__Result
                             ) -> List[str]:
        seen : Dict[str, int] = {}
        for node in load_result.nodes:
            label = str(node.label)
            seen[label] = seen.get(label, 0) + 1
        return sorted([label for label, count in seen.items() if count > 1])

    def find_broken_refs(self, files: List[tuple]) -> List[str]:
        from issues_fs.issues.issues_file.Parser__Issues_File import Parser__Issues_File
        parser    = Parser__Issues_File()
        all_labels : Set[str] = set()
        all_refs   : Set[str] = set()

        for content, source_file in files:
            result = parser.parse(content, source_file)
            for issue in result.issues:
                all_labels.add(issue.label)
                for ref in issue.cross_refs:
                    all_refs.add(ref)

        return sorted([ref for ref in all_refs if ref not in all_labels])

    def find_mixed_indent(self, files: List[tuple]) -> List[str]:
        mixed = []
        for content, source_file in files:
            has_tab   = False
            has_space = False
            for line in content.split('\n'):
                if line and not line.strip().startswith('#'):
                    if line[0] == '\t':
                        has_tab = True
                    elif line[0] == ' ' and line.strip():
                        has_space = True
            if has_tab and has_space:
                mixed.append(source_file)
        return mixed

    def format_report(self, summary: Schema__Issues_File__Check__Summary) -> str:
        lines = []
        lines.append('# issues-fs check')
        lines.append('')

        status = 'PASS' if summary.is_valid is True else 'FAIL'
        lines.append(f'Status: {status}')
        lines.append(f'Files:  {len(summary.files_checked)}')
        lines.append(f'Issues: {summary.total_issues}')
        lines.append(f'Errors: {summary.total_errors}')
        lines.append('')

        if summary.issues_by_type:
            lines.append('By type:')
            for t in sorted(summary.issues_by_type.keys()):
                lines.append(f'  {t}: {summary.issues_by_type[t]}')
            lines.append('')

        if summary.issues_by_status:
            lines.append('By status:')
            for s in sorted(summary.issues_by_status.keys()):
                lines.append(f'  {s}: {summary.issues_by_status[s]}')
            lines.append('')

        if summary.duplicate_labels:
            lines.append('Duplicate labels:')
            for label in summary.duplicate_labels:
                lines.append(f'  - {label}')
            lines.append('')

        if summary.broken_refs:
            lines.append('Broken cross-references:')
            for ref in summary.broken_refs:
                lines.append(f'  - {ref}')
            lines.append('')

        if summary.mixed_indent:
            lines.append('Mixed indentation (tabs + spaces):')
            for f in summary.mixed_indent:
                lines.append(f'  - {f}')
            lines.append('')

        return '\n'.join(lines)
