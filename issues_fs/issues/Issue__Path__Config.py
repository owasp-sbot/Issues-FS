# ═══════════════════════════════════════════════════════════════════════════════
# Issue__Path__Config - Configuration for issue tracking paths
# Provides the default issues directory path based on project structure
# ═══════════════════════════════════════════════════════════════════════════════
import mgraph_ai_ui_html_transformation_workbench
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.utils.Files                                                      import path_combine, folder_exists, folder_create


class Issue__Path__Config(Type_Safe):                                            # Issue path configuration

    @classmethod
    def default_issues_path(cls) -> Safe_Str__File__Path:                                    # Get default issues directory
        root_path   = mgraph_ai_ui_html_transformation_workbench.path
        issues_path = path_combine(root_path, '../docs/dev-briefs/issues')
        return issues_path

    @classmethod
    def ensure_issues_directory(cls, path: Safe_Str__File__Path = None) -> Safe_Str__File__Path:         # Create issues directory if needed
        if path is None:
            path = cls.default_issues_path()
        if folder_exists(path) is False:
            folder_create(path)
        return path
