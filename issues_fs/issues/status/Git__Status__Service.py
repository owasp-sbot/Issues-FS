# ═══════════════════════════════════════════════════════════════════════════════
# Git__Status__Service - Git repository integration status
# Detects git repository and provides integration information
# ═══════════════════════════════════════════════════════════════════════════════

import subprocess
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                        import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                                import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path

from mgraph_ai_ui_html_transformation_workbench.schemas.status.Schema__Git__Status import Schema__Git__Status


class Git__Status__Service(Type_Safe):                                           # Git status service
    root_path : Safe_Str__File__Path = ''                                              # Path to check for git

    # ═══════════════════════════════════════════════════════════════════════════════
    # Main Status Method
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_status(self) -> Schema__Git__Status:                                 # Get git status
        work_dir = str(self.root_path) if self.root_path else None

        is_git_repo = self._is_git_repository(work_dir)
        if not is_git_repo:
            return Schema__Git__Status(is_git_repo = False)

        git_root       = self._get_git_root(work_dir)
        current_branch = self._get_current_branch(work_dir)
        current_commit = self._get_current_commit(work_dir)
        is_dirty       = self._is_dirty(work_dir)
        issues_tracked = self._is_issues_tracked(work_dir)
        untracked      = self._count_untracked_issues(work_dir)
        modified       = self._count_modified_issues(work_dir)
        remote_name    = self._get_remote_name(work_dir)
        remote_url     = self._get_remote_url(work_dir, remote_name)

        return Schema__Git__Status(is_git_repo      = True                                  ,
                                   git_root         = Safe_Str__Text(git_root)              ,
                                   current_branch   = Safe_Str__Text(current_branch)        ,
                                   current_commit   = Safe_Str__Text(current_commit)        ,
                                   is_dirty         = is_dirty                              ,
                                   issues_tracked   = issues_tracked                        ,
                                   untracked_issues = Safe_UInt(untracked)                  ,
                                   modified_issues  = Safe_UInt(modified)                   ,
                                   remote_name      = Safe_Str__Text(remote_name)           ,
                                   remote_url       = Safe_Str__Text(remote_url)            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Git Command Helpers
    # ═══════════════════════════════════════════════════════════════════════════════

    def _run_git_command(self, args: list, work_dir: str = None) -> str:         # Run git command
        try:
            result = subprocess.run(['git'] + args                                          ,
                                    cwd             = work_dir                              ,
                                    capture_output  = True                                  ,
                                    text            = True                                  ,
                                    timeout         = 5                                     )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # Status Detection Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _is_git_repository(self, work_dir: str = None) -> bool:                  # Check if git repo
        result = self._run_git_command(['rev-parse', '--git-dir'], work_dir)
        return bool(result)

    def _get_git_root(self, work_dir: str = None) -> str:                        # Get git root path
        return self._run_git_command(['rev-parse', '--show-toplevel'], work_dir)

    def _get_current_branch(self, work_dir: str = None) -> str:                  # Get current branch
        return self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'], work_dir)

    def _get_current_commit(self, work_dir: str = None) -> str:                  # Get short commit hash
        return self._run_git_command(['rev-parse', '--short', 'HEAD'], work_dir)

    def _is_dirty(self, work_dir: str = None) -> bool:                           # Check for uncommitted changes
        result = self._run_git_command(['status', '--porcelain'], work_dir)
        return bool(result)

    def _is_issues_tracked(self, work_dir: str = None) -> bool:                  # Check if .issues is tracked
        result = self._run_git_command(['ls-files', '.issues'], work_dir)
        return bool(result)

    def _count_untracked_issues(self, work_dir: str = None) -> int:              # Count untracked issue files
        result = self._run_git_command(['ls-files', '--others', '--exclude-standard', '.issues'], work_dir)
        if result:
            return len(result.splitlines())
        return 0

    def _count_modified_issues(self, work_dir: str = None) -> int:               # Count modified issue files
        result = self._run_git_command(['diff', '--name-only', '.issues'], work_dir)
        if result:
            return len(result.splitlines())
        return 0

    def _get_remote_name(self, work_dir: str = None) -> str:                     # Get first remote name
        result = self._run_git_command(['remote'], work_dir)
        if result:
            remotes = result.splitlines()
            if remotes:
                return remotes[0]
        return ''

    def _get_remote_url(self, work_dir: str = None, remote_name: str = '') -> str:  # Get remote URL
        if not remote_name:
            return ''
        return self._run_git_command(['remote', 'get-url', remote_name], work_dir)
