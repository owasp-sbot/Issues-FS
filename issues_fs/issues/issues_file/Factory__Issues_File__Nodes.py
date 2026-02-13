# ═══════════════════════════════════════════════════════════════════════════════
# Factory__Issues_File__Nodes - Converts parsed .issues lines into Schema__Node
# Maps the 3-field flat format to the full 14-field Schema__Node structure
# ═══════════════════════════════════════════════════════════════════════════════

import re
from typing                                                                             import List, Tuple
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text            import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                        import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now        import Timestamp_Now
from issues_fs.issues.issues_file.Schema__Issues_File__Line                             import Schema__Issues_File__Line
from issues_fs.issues.issues_file.Schema__Issues_File__Error                            import Schema__Issues_File__Error
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                      import Safe_Str__Node_Type, Safe_Str__Node_Label, Safe_Str__Status, Safe_Str__Link_Verb
from issues_fs.schemas.graph.Schema__Node                                               import Schema__Node
from issues_fs.schemas.graph.Schema__Node__Link                                         import Schema__Node__Link
from issues_fs.schemas.safe_str.Safe_Str__Issue__Node__Description                      import Safe_Str__Issue__Node__Description

LABEL_INDEX_PATTERN = re.compile(r'-(\d{1,5})$')


class Factory__Issues_File__Nodes(Type_Safe):

    def create_nodes(self, parsed_lines: List[Schema__Issues_File__Line]
                    ) -> Tuple[List[Schema__Node], List[Schema__Issues_File__Error]]:
        nodes  : List[Schema__Node]              = []
        errors : List[Schema__Issues_File__Error] = []

        node_map = {}                                                           # label -> Schema__Node for link wiring

        for line in parsed_lines:
            node, error = self.create_node(line)
            if error is not None:
                errors.append(error)
                continue
            nodes.append(node)
            node_map[line.label] = node

        # second pass: wire parent-child links and cross-references
        for line in parsed_lines:
            if line.label not in node_map:
                continue
            node = node_map[line.label]

            if line.parent_label and line.parent_label in node_map:             # parent-child link
                parent = node_map[line.parent_label]
                link   = Schema__Node__Link(link_type_id = Obj_Id()                                     ,
                                            verb         = Safe_Str__Link_Verb('has-task')               ,
                                            target_id    = Obj_Id(str(node.node_id))                     ,
                                            target_label = Safe_Str__Node_Label(line.label)              ,
                                            created_at   = Timestamp_Now()                               )
                parent.links.append(link)

            for ref_label in line.cross_refs:                                   # cross-reference links
                if ref_label in node_map:
                    target = node_map[ref_label]
                    link   = Schema__Node__Link(link_type_id = Obj_Id()                                  ,
                                                verb         = Safe_Str__Link_Verb('relates-to')          ,
                                                target_id    = Obj_Id(str(target.node_id))                ,
                                                target_label = Safe_Str__Node_Label(ref_label)            ,
                                                created_at   = Timestamp_Now()                            )
                    node.links.append(link)

        return (nodes, errors)

    def create_node(self, line: Schema__Issues_File__Line
                   ) -> Tuple[Schema__Node, Schema__Issues_File__Error]:
        try:
            node_index = self.extract_index(line.label)
            now        = Timestamp_Now()

            node = Schema__Node(node_id     = Obj_Id()                                               ,
                                node_type   = Safe_Str__Node_Type(line.issue_type)                    ,
                                node_index  = Safe_UInt(node_index)                                   ,
                                label       = Safe_Str__Node_Label(line.label)                        ,
                                title       = Safe_Str__Text(line.description)                        ,
                                description = Safe_Str__Issue__Node__Description(line.description)    ,
                                status      = Safe_Str__Status(line.status)                           ,
                                created_at  = now                                                     ,
                                updated_at  = now                                                     ,
                                created_by  = Obj_Id()                                                ,
                                tags        = []                                                      ,
                                links       = []                                                      ,
                                properties  = {}                                                      )
            return (node, None)
        except Exception as e:
            error = Schema__Issues_File__Error(line_number = line.line_number ,
                                               raw_line    = f'{line.label} | {line.status} | {line.description}',
                                               message     = str(e)          )
            return (None, error)

    def extract_index(self, label: str) -> int:                                 # Extract number from label tail
        match = LABEL_INDEX_PATTERN.search(label)
        if match:
            return int(match.group(1))
        return 0
