# ═══════════════════════════════════════════════════════════════════════════════
# Path__Handler__Issues - Custom path handler for issue tracking file structure
# Generates paths like: {Issue-NNN}.json, issues.json, labels.json
# ═══════════════════════════════════════════════════════════════════════════════


from osbot_utils.utils.Files                                                        import path_combine_safe
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                      import type_safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Name   import Safe_Str__File__Name
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path   import Safe_Str__File__Path
from mgraph_ai_ui_html_transformation_workbench.schemas.safe_str.Safe_Str__Issue_Id import Safe_Str__Issue_Id


class Path__Handler__Issues(Type_Safe):                                          # Path handler for issues
    base_path : Safe_Str__File__Path                                             # Optional prefix (empty for root)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Issue Paths
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def path_for_issue(self,
                       issue_id: Safe_Str__Issue_Id
                  ) -> Safe_Str__File__Path:          # Path to issue JSON file
        if self.base_path:
            return path_combine_safe(self.base_path, f"{issue_id}.json")
        return f"{issue_id}.json"

    @type_safe
    def path_for_issues_index(self) -> Safe_Str__File__Path:                                 # Path to issues.json index
        if self.base_path:
            return f"{self.base_path}/issues.json"
        return "issues.json"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Label Paths
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def path_for_labels(self) -> Safe_Str__File__Path:                                       # Path to labels.json
        if self.base_path:
            return path_combine_safe(self.base_path, "labels.json")
        return "labels.json"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Attachment Paths (for future use)
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def path_for_attachment(self                              ,                  # Path to attachment file
                            issue_id : Safe_Str__Issue_Id     ,
                            filename : Safe_Str__File__Name
                       ) -> Safe_Str__File__Path:
        if self.base_path:
            return path_combine_safe(self.base_path,f"attachments/{issue_id}/{filename}")
        return f"attachments/{issue_id}/{filename}"
