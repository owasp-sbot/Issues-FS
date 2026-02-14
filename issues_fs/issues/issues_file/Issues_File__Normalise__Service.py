# ═══════════════════════════════════════════════════════════════════════════════
# Issues_File__Normalise__Service - Exports .issues to JSON issue structure
# Converts the flat .issues format into data/{type}/{label}/issue.json files
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Dict, List, Tuple
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Json                                                     import json_dumps
from issues_fs.issues.issues_file.Issues_File__Loader__Service                  import Issues_File__Loader__Service
from issues_fs.schemas.graph.Schema__Node                                       import Schema__Node


class Schema__Normalise__Result(Type_Safe):
    files_written : List[str]                                                   # paths of JSON files created
    nodes_written : int                                                         # total nodes exported
    errors        : List[str]                                                   # any export errors


class Issues_File__Normalise__Service(Type_Safe):
    loader : Issues_File__Loader__Service

    def normalise_to_dict(self, content: str, source_file: str = ''
                         ) -> Tuple[Dict[str, str], List[str]]:
        load_result = self.loader.load_content(content, source_file)
        file_map    = {}                                                        # path -> json content
        errors      = [f'line {e.line_number}: {e.message}' for e in load_result.errors]

        for node in load_result.nodes:
            path    = self.node_to_path(node)
            content = self.node_to_json(node)
            file_map[path] = content

        return (file_map, errors)

    def normalise_multiple(self, files: List[Tuple[str, str]]
                          ) -> Tuple[Dict[str, str], List[str]]:
        all_files  : Dict[str, str] = {}
        all_errors : List[str]      = []

        for content, source_file in files:
            file_map, errors = self.normalise_to_dict(content, source_file)
            all_files.update(file_map)
            all_errors.extend(errors)

        return (all_files, all_errors)

    def node_to_path(self, node: Schema__Node) -> str:                          # data/{type}/{label}/issue.json
        node_type = str(node.node_type)
        label     = str(node.label)
        return f'data/{node_type}/{label}/issue.json'

    def node_to_json(self, node: Schema__Node) -> str:                          # Serialize node to JSON string
        data = {}
        data['node_id']     = str(node.node_id)
        data['node_type']   = str(node.node_type)
        data['node_index']  = int(node.node_index)
        data['label']       = str(node.label)
        data['title']       = str(node.title)
        data['description'] = str(node.description)
        data['status']      = str(node.status)
        data['created_at']  = str(node.created_at)
        data['updated_at']  = str(node.updated_at)
        data['created_by']  = str(node.created_by)
        data['tags']        = [str(t) for t in node.tags]
        data['links']       = []
        for link in node.links:
            data['links'].append({'link_type_id' : str(link.link_type_id) ,
                                  'verb'         : str(link.verb)         ,
                                  'target_id'    : str(link.target_id)    ,
                                  'target_label' : str(link.target_label) ,
                                  'created_at'   : str(link.created_at)   })
        data['properties'] = dict(node.properties) if node.properties else {}

        return json_dumps(data, indent=2)
