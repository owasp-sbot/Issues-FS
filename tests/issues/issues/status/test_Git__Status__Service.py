# ═══════════════════════════════════════════════════════════════════════════════
# test_Git__Status__Service - Unit tests for Git integration status
# Tests git repository detection and status reporting
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                              import TestCase
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path          import Safe_Str__File__Path
from mgraph_ai_ui_html_transformation_workbench.schemas.status.Schema__Git__Status         import Schema__Git__Status
from mgraph_ai_ui_html_transformation_workbench.service.issues.status.Git__Status__Service import Git__Status__Service


class test_Git__Status__Service(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test service initialization
        service = Git__Status__Service()

        assert type(service)    is Git__Status__Service
        assert str(service.root_path) == ''

    def test__init____with_root_path(self):                                      # Test with root path
        service = Git__Status__Service(root_path=Safe_Str__File__Path('/some/path'))

        assert str(service.root_path) == '/some/path'

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_status Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_status__returns_schema(self):                                  # Test return type
        service = Git__Status__Service()

        status = service.get_status()

        assert type(status) is Schema__Git__Status

    def test__get_status__non_git_directory(self):                               # Test in non-git directory
        service = Git__Status__Service(root_path=Safe_Str__File__Path('/tmp'))

        status = service.get_status()

        # /tmp is unlikely to be a git repo
        # If it happens to be, the test still passes
        assert type(status) is Schema__Git__Status

    def test__get_status__has_all_fields(self):                                  # Test all fields present
        service = Git__Status__Service()

        status = service.get_status()

        assert hasattr(status, 'is_git_repo')
        assert hasattr(status, 'git_root')
        assert hasattr(status, 'current_branch')
        assert hasattr(status, 'current_commit')
        assert hasattr(status, 'is_dirty')
        assert hasattr(status, 'issues_tracked')
        assert hasattr(status, 'untracked_issues')
        assert hasattr(status, 'modified_issues')
        assert hasattr(status, 'remote_name')
        assert hasattr(status, 'remote_url')

    def test__get_status__field_types(self):                                     # Test field types
        service = Git__Status__Service()

        status = service.get_status()

        assert type(status.is_git_repo)       is bool
        assert type(status.is_dirty)          is bool
        assert type(status.issues_tracked)    is bool

    # ═══════════════════════════════════════════════════════════════════════════════
    # Git Command Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___run_git_command__invalid_command(self):                           # Test invalid git command
        service = Git__Status__Service()

        result = service._run_git_command(['invalid-command-xyz'])

        assert result == ''                                                      # Returns empty on error

    def test___run_git_command__timeout(self):                                   # Test command with bad dir
        service = Git__Status__Service()

        result = service._run_git_command(['status'], '/nonexistent/path')

        assert result == ''                                                      # Returns empty on error

    # ═══════════════════════════════════════════════════════════════════════════════
    # Detection Method Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___is_git_repository__non_git(self):                                 # Test non-git directory
        service = Git__Status__Service()

        # Use a path that's unlikely to be a git repo
        result = service._is_git_repository('/tmp/unlikely_git_' + str(id(self)))

        assert result is False

    def test___get_git_root__non_git(self):                                      # Test git root in non-git
        service = Git__Status__Service()

        result = service._get_git_root('/tmp/unlikely_git_' + str(id(self)))

        assert result == ''

    def test___get_current_branch__non_git(self):                                # Test branch in non-git
        service = Git__Status__Service()

        result = service._get_current_branch('/tmp/unlikely_git_' + str(id(self)))

        assert result == ''

    def test___get_current_commit__non_git(self):                                # Test commit in non-git
        service = Git__Status__Service()

        result = service._get_current_commit('/tmp/unlikely_git_' + str(id(self)))

        assert result == ''

    def test___is_dirty__non_git(self):                                          # Test dirty in non-git
        service = Git__Status__Service()

        result = service._is_dirty('/tmp/unlikely_git_' + str(id(self)))

        assert result is False

    def test___is_issues_tracked__non_git(self):                                 # Test issues tracked in non-git
        service = Git__Status__Service()

        result = service._is_issues_tracked('/tmp/unlikely_git_' + str(id(self)))

        assert result is False

    def test___count_untracked_issues__non_git(self):                            # Test untracked count in non-git
        service = Git__Status__Service()

        result = service._count_untracked_issues('/tmp/unlikely_git_' + str(id(self)))

        assert result == 0

    def test___count_modified_issues__non_git(self):                             # Test modified count in non-git
        service = Git__Status__Service()

        result = service._count_modified_issues('/tmp/unlikely_git_' + str(id(self)))

        assert result == 0

    def test___get_remote_name__non_git(self):                                   # Test remote name in non-git
        service = Git__Status__Service()

        result = service._get_remote_name('/tmp/unlikely_git_' + str(id(self)))

        assert result == ''

    def test___get_remote_url__no_remote(self):                                  # Test remote URL with no remote
        service = Git__Status__Service()

        result = service._get_remote_url('/tmp', '')

        assert result == ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests (if running in a git repo)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_status__in_actual_git_repo(self):                              # Test in actual git repo
        service = Git__Status__Service(root_path=Safe_Str__File__Path('.'))

        status = service.get_status()

        # If we're running in a git repo, we should get valid data
        # If not, this still passes (is_git_repo will be False)
        if status.is_git_repo:
            assert str(status.current_branch) != ''
            assert str(status.current_commit) != ''
            assert str(status.git_root)       != ''
