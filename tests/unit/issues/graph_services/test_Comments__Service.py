# ═══════════════════════════════════════════════════════════════════════════════
# Test cases for Comments API
# Run with: pytest tests/unit/test_comments_api.py -v
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from issues_fs.issues.graph_services.Comments__Service             import Comments__Service
from issues_fs.issues.graph_services.Graph__Repository__Factory    import Graph__Repository__Factory
from issues_fs.issues.graph_services.Node__Service                 import Node__Service
from issues_fs.issues.graph_services.Type__Service                 import Type__Service
from issues_fs.schemas.graph.Safe_Str__Graph_Types                 import Safe_Str__Node_Type, Safe_Str__Node_Label
from issues_fs.schemas.graph.Schema__Node__Create__Request         import Schema__Node__Create__Request
from issues_fs.schemas.issues.Schema__Comment                      import Schema__Comment__Create__Request, Schema__Comment__Update__Request


class test_Comments__Service(TestCase):
    """Test Comments__Service CRUD operations."""

    @classmethod
    def setUpClass(cls):
        cls.repository       = Graph__Repository__Factory.create_memory()
        cls.type_service     = Type__Service    (repository=cls.repository)
        cls.node_service     = Node__Service    (repository=cls.repository)
        cls.comments_service = Comments__Service(repository=cls.repository)

        cls.type_service.initialize_default_types()

        # Create a test node
        create_request = Schema__Node__Create__Request(title     = 'Test Node for Comments',
                                                       node_type = 'task'                  )
        create_response = cls.node_service.create_node(create_request)
        cls.test_node_label = create_response.node.label
        cls.test_node_type  = create_response.node.node_type

    # ─────────────────────────────────────────────────────────────────────────────
    # List Comments
    # ─────────────────────────────────────────────────────────────────────────────

    def test_list_comments__empty(self):
        response = self.comments_service.list_comments(node_type = self.test_node_type  ,
                                                       label     = self.test_node_label)
        assert response.success  is True
        assert response.total    == 0
        assert response.comments == []

    def test_list_comments__node_not_found(self):

        response = self.comments_service.list_comments(node_type = Safe_Str__Node_Type('task')            ,
                                                       label     = Safe_Str__Node_Label('NonExistent-99'))
        assert response.success is False
        assert 'not found' in response.message.lower()

    # ─────────────────────────────────────────────────────────────────────────────
    # Create Comment
    # ─────────────────────────────────────────────────────────────────────────────

    def test_create_comment__success(self):
        request = Schema__Comment__Create__Request(author = 'human'          ,
                                                   text   = 'This is a test comment')
        response = self.comments_service.create_comment(node_type = self.test_node_type  ,
                                                        label     = self.test_node_label ,
                                                        request   = request              )

        assert response.success is True
        assert response.comment is not None
        assert str(response.comment.author) == 'human'
        assert 'test comment' in str(response.comment.text)
        assert response.comment.id is not None                                   # Server generated ID
        assert self.comments_service.delete_comment(node_type  = self.test_node_type ,
                                                    label      = self.test_node_label ,
                                                    comment_id = response.comment.id  ).success is True

    def test_create_comment__empty_text_fails(self):
        request = Schema__Comment__Create__Request(author = 'human', text = '')
        response = self.comments_service.create_comment(node_type = self.test_node_type  ,
                                                        label     = self.test_node_label ,
                                                        request   = request     )

        assert response.success is False
        assert 'required' in response.message.lower()

    def test_create_comment__empty_author_fails(self):
        request = Schema__Comment__Create__Request(author = '', text = 'Some text')
        response = self.comments_service.create_comment(
            node_type = self.test_node_type  ,
            label     = self.test_node_label ,
            request   = request
        )

        assert response.success is False
        assert 'required' in response.message.lower()

    # ─────────────────────────────────────────────────────────────────────────────
    # Get Comment
    # ─────────────────────────────────────────────────────────────────────────────

    def test_get_comment__success(self):
        # First create a comment
        create_request = Schema__Comment__Create__Request(author = 'test-user'   ,
                                                          text   = 'Findable comment')
        create_response = self.comments_service.create_comment(
            node_type = self.test_node_type  ,
            label     = self.test_node_label ,
            request   = create_request
        )
        comment_id = str(create_response.comment.id)

        # Now get it
        response = self.comments_service.get_comment(
            node_type  = self.test_node_type  ,
            label      = self.test_node_label ,
            comment_id = comment_id
        )

        assert response.success is True
        assert str(response.comment.id) == comment_id
        assert 'Findable' in str(response.comment.text)

        assert self.comments_service.delete_comment(node_type  = self.test_node_type ,
                                                    label      = self.test_node_label ,
                                                    comment_id = response.comment.id  ).success is True

    def test_get_comment__not_found(self):
        response = self.comments_service.get_comment(
            node_type  = self.test_node_type  ,
            label      = self.test_node_label ,
            comment_id = 'nonexistent-id'
        )

        assert response.success is False
        assert 'not found' in response.message.lower()

    # ─────────────────────────────────────────────────────────────────────────────
    # Update Comment
    # ─────────────────────────────────────────────────────────────────────────────

    def test_update_comment__success(self):
        # First create a comment
        create_request = Schema__Comment__Create__Request(author = 'editor'       ,
                                                          text   = 'Original text')
        create_response = self.comments_service.create_comment(
            node_type = self.test_node_type  ,
            label     = self.test_node_label ,
            request   = create_request
        )
        comment_id = str(create_response.comment.id)

        # Update it
        update_request = Schema__Comment__Update__Request(text = 'Updated text')
        response = self.comments_service.update_comment(
            node_type  = self.test_node_type  ,
            label      = self.test_node_label ,
            comment_id = comment_id           ,
            request    = update_request
        )

        assert response.success is True
        assert 'Updated text' in str(response.comment.text)
        assert str(response.comment.author) == 'editor'                          # Author preserved

    def test_update_comment__not_found(self):
        update_request = Schema__Comment__Update__Request(text = 'New text')
        response = self.comments_service.update_comment(
            node_type  = self.test_node_type  ,
            label      = self.test_node_label ,
            comment_id = 'nonexistent-id'     ,
            request    = update_request
        )

        assert response.success is False
        assert 'not found' in response.message.lower()

    # ─────────────────────────────────────────────────────────────────────────────
    # Delete Comment
    # ─────────────────────────────────────────────────────────────────────────────

    def test_delete_comment__success(self):
        # First create a comment
        create_request = Schema__Comment__Create__Request(author = 'deleter'       ,
                                                          text   = 'To be deleted')
        create_response = self.comments_service.create_comment(
            node_type = self.test_node_type  ,
            label     = self.test_node_label ,
            request   = create_request
        )
        comment_id = str(create_response.comment.id)

        # Delete it
        response = self.comments_service.delete_comment(
            node_type  = self.test_node_type  ,
            label      = self.test_node_label ,
            comment_id = comment_id
        )

        assert response.success is True
        assert response.deleted is True
        assert response.comment_id == comment_id

        # Verify it's gone
        get_response = self.comments_service.get_comment(
            node_type  = self.test_node_type  ,
            label      = self.test_node_label ,
            comment_id = comment_id
        )
        assert get_response.success is False

    def test_delete_comment__not_found(self):
        response = self.comments_service.delete_comment(
            node_type  = self.test_node_type  ,
            label      = self.test_node_label ,
            comment_id = 'nonexistent-id'
        )

        assert response.success is False
        assert response.deleted is False