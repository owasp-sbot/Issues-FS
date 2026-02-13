# ═══════════════════════════════════════════════════════════════════════════════
# Issues_File__Loader__Service - Top-level orchestrator for .issues file loading
# Parses .issues files and converts them into Schema__Node instances
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import List, Tuple
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from issues_fs.issues.issues_file.Parser__Issues_File                           import Parser__Issues_File
from issues_fs.issues.issues_file.Factory__Issues_File__Nodes                   import Factory__Issues_File__Nodes
from issues_fs.issues.issues_file.Schema__Issues_File__Error                    import Schema__Issues_File__Error
from issues_fs.issues.issues_file.Schema__Issues_File__Result                   import Schema__Issues_File__Result
from issues_fs.schemas.graph.Schema__Node                                       import Schema__Node


class Schema__Issues_File__Load__Result(Type_Safe):
    nodes       : List[Schema__Node]                                            # all created nodes
    errors      : List[Schema__Issues_File__Error]                              # all errors from parsing + creation
    files_loaded: List[str]                                                     # which .issues files were processed
    total_issues: int                                                           # total issue count


class Issues_File__Loader__Service(Type_Safe):
    parser       : Parser__Issues_File
    node_factory : Factory__Issues_File__Nodes

    def load_content(self, content: str, source_file: str = ''
                    ) -> Schema__Issues_File__Load__Result:
        parse_result = self.parser.parse(content, source_file)
        nodes, create_errors = self.node_factory.create_nodes(parse_result.issues)

        all_errors = list(parse_result.errors) + list(create_errors)

        return Schema__Issues_File__Load__Result(nodes        = nodes                ,
                                                  errors       = all_errors           ,
                                                  files_loaded = [source_file]        ,
                                                  total_issues = len(nodes)           )

    def load_multiple(self, files: List[Tuple[str, str]]
                     ) -> Schema__Issues_File__Load__Result:
        all_nodes  : List[Schema__Node]              = []
        all_errors : List[Schema__Issues_File__Error] = []
        all_files  : List[str]                        = []

        for content, source_file in files:
            result = self.load_content(content, source_file)
            all_nodes.extend(result.nodes)
            all_errors.extend(result.errors)
            all_files.append(source_file)

        return Schema__Issues_File__Load__Result(nodes        = all_nodes     ,
                                                  errors       = all_errors    ,
                                                  files_loaded = all_files     ,
                                                  total_issues = len(all_nodes))
