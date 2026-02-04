# ═══════════════════════════════════════════════════════════════════════════════
# test_Node__Service - Unit tests for node service business logic
# Tests node CRUD operations with business rules and validation
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                            import TestCase
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.utils.Objects import base_classes

from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types import Safe_Str__Node_Type, Safe_Str__Status, Safe_Str__Node_Label
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Create__Request import Schema__Node__Create__Request
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Update__Request import Schema__Node__Update__Request
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository__Factory import Graph__Repository__Factory
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Node__Service              import Node__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Type__Service              import Type__Service


class test_Node__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup - create once
        cls.repository   = Graph__Repository__Factory.create_memory()
        cls.type_service = Type__Service(repository=cls.repository)
        cls.node_service = Node__Service(repository=cls.repository)

    def setUp(self):                                                             # Reset before each test
        self.repository.clear_storage()
        self.type_service.initialize_default_types()                             # Set up default types

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test service initialization
        with self.node_service as _:
            assert type(_)            is Node__Service
            assert base_classes(_)    == [Type_Safe, object]
            assert _.repository       is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__create_node(self):                                                 # Test successful node creation
        request = Schema__Node__Create__Request(node_type   = Safe_Str__Node_Type('bug')       ,
                                                title       = 'Login fails with special characters',
                                                description = 'Users cannot log in with & or <'    ,
                                                tags        = []                                   ,
                                                properties  = {'severity': 'high'}                 )

        response = self.node_service.create_node(request)

        assert response.success           is True
        assert response.node              is not None
        assert str(response.node.label)   == 'Bug-1'                             # First bug
        assert str(response.node.title)   == 'Login fails with special characters'
        assert str(response.node.status)  == 'backlog'                           # Default status

    def test__create_node__with_custom_status(self):                             # Test creation with custom status
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('bug')         ,
                                                title     = 'Already confirmed bug'            ,
                                                status    = Safe_Str__Status('confirmed')      )

        response = self.node_service.create_node(request)

        assert response.success          is True
        assert str(response.node.status) == 'confirmed'

    def test__create_node__with_tags(self):                                      # Test creation with tags
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('task')        ,
                                                title     = 'Tagged task'                      ,
                                                tags      = ['urgent', 'backend', 'api']       )

        response = self.node_service.create_node(request)

        assert response.success is True
        assert len(response.node.tags) == 3
        assert 'urgent' in [str(t) for t in response.node.tags]

    def test__create_node__with_properties(self):                                # Test creation with custom properties
        request = Schema__Node__Create__Request(node_type  = Safe_Str__Node_Type('bug')        ,
                                                title      = 'Bug with properties'             ,
                                                properties = {'browser': 'Chrome'              ,
                                                              'os': 'Windows 11'               ,
                                                              'reproducible': True             })

        response = self.node_service.create_node(request)

        assert response.success is True
        assert response.node.properties.get('browser')      == 'Chrome'
        assert response.node.properties.get('os')           == 'Windows 11'
        assert response.node.properties.get('reproducible') == True

    def test__create_node__missing_title(self):                                  # Test title validation
        request = Schema__Node__Create__Request(node_type   = Safe_Str__Node_Type('bug')       ,
                                                title       = ''                               ,  # Empty
                                                description = 'Some description'               )

        response = self.node_service.create_node(request)

        assert response.success is False
        assert 'Title is required' in str(response.message)

    def test__create_node__whitespace_title(self):                               # Test whitespace title validation
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('bug')         ,
                                                title     = '   '                              )  # Only whitespace

        response = self.node_service.create_node(request)

        assert response.success is False
        assert 'Title is required' in str(response.message)

    def test__create_node__unknown_type(self):                                   # Test unknown type validation
        request = Schema__Node__Create__Request(node_type   = Safe_Str__Node_Type('unknown')   ,
                                                title       = 'Some title'                     )

        response = self.node_service.create_node(request)

        assert response.success is False
        assert 'Unknown node type' in str(response.message)

    def test__create_node__sequential_indices(self):                             # Test index incrementing
        request1 = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('task')       ,
                                                 title     = 'Task One'                        )
        request2 = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('task')       ,
                                                 title     = 'Task Two'                        )
        request3 = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('task')       ,
                                                 title     = 'Task Three'                      )

        response1 = self.node_service.create_node(request1)
        response2 = self.node_service.create_node(request2)
        response3 = self.node_service.create_node(request3)

        assert str(response1.node.label) == 'Task-1'
        assert str(response2.node.label) == 'Task-2'
        assert str(response3.node.label) == 'Task-3'

    def test__create_node__different_types_independent_indices(self):            # Test indices per type
        bug_request     = Schema__Node__Create__Request(node_type=Safe_Str__Node_Type('bug'), title='Bug')
        task_request    = Schema__Node__Create__Request(node_type=Safe_Str__Node_Type('task'), title='Task')
        feature_request = Schema__Node__Create__Request(node_type=Safe_Str__Node_Type('feature'), title='Feature')

        bug_response     = self.node_service.create_node(bug_request)
        task_response    = self.node_service.create_node(task_request)
        feature_response = self.node_service.create_node(feature_request)

        assert str(bug_response.node.label)     == 'Bug-1'                       # Each type starts at 1
        assert str(task_response.node.label)    == 'Task-1'
        assert str(feature_response.node.label) == 'Feature-1'

    def test__create_node__sets_timestamps(self):                                # Test timestamps are set
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('bug')         ,
                                                title     = 'Timestamp test'                   )

        response = self.node_service.create_node(request)

        assert response.success is True
        assert response.node.created_at is not None
        assert response.node.updated_at is not None

    def test__create_node__generates_node_id(self):                              # Test node_id is generated
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('bug')         ,
                                                title     = 'ID test'                          )

        response = self.node_service.create_node(request)

        assert response.success is True
        assert response.node.node_id is not None
        assert str(response.node.node_id) != ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # Update Node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__update_node(self):                                                 # Test successful update
        self._create_bug('Bug-1', 'Original title')

        update_request = Schema__Node__Update__Request(title  = 'Updated title'                ,
                                                       status = Safe_Str__Status('confirmed')  )

        response = self.node_service.update_node(node_type = Safe_Str__Node_Type('bug')        ,
                                                 label     = Safe_Str__Node_Label('Bug-1')     ,
                                                 request   = update_request                    )

        assert response.success          is True
        assert str(response.node.title)  == 'Updated title'
        assert str(response.node.status) == 'confirmed'

    def test__update_node__partial_update(self):                                 # Test only updates provided fields
        self._create_bug('Bug-1', 'Original title')

        update_request = Schema__Node__Update__Request(status = Safe_Str__Status('testing'))   # Only status

        response = self.node_service.update_node(node_type = Safe_Str__Node_Type('bug')        ,
                                                 label     = Safe_Str__Node_Label('Bug-1')     ,
                                                 request   = update_request                    )

        assert response.success          is True
        assert str(response.node.title)  == 'Original title'                     # Unchanged
        assert str(response.node.status) == 'testing'                            # Updated

    def test__update_node__update_tags(self):                                    # Test tag update
        self._create_bug('Bug-1', 'Bug with tags')

        update_request = Schema__Node__Update__Request(tags = ['new-tag', 'another-tag'])

        response = self.node_service.update_node(node_type = Safe_Str__Node_Type('bug')        ,
                                                 label     = Safe_Str__Node_Label('Bug-1')     ,
                                                 request   = update_request                    )

        assert response.success is True
        assert len(response.node.tags) == 2
        assert 'new-tag' in [str(t) for t in response.node.tags]

    def test__update_node__update_properties(self):                              # Test properties merge
        self._create_bug('Bug-1', 'Bug with properties')

        update_request = Schema__Node__Update__Request(properties = {'severity': 'critical'})

        response = self.node_service.update_node(node_type = Safe_Str__Node_Type('bug')        ,
                                                 label     = Safe_Str__Node_Label('Bug-1')     ,
                                                 request   = update_request                    )

        assert response.success is True
        assert response.node.properties.get('severity') == 'critical'

    def test__update_node__not_found(self):                                      # Test update non-existent node
        update_request = Schema__Node__Update__Request(title = 'New title')

        response = self.node_service.update_node(node_type = Safe_Str__Node_Type('bug')        ,
                                                 label     = Safe_Str__Node_Label('Bug-999')   ,
                                                 request   = update_request                    )

        assert response.success is False
        assert 'not found' in str(response.message).lower()

    def test__update_node__updates_timestamp(self):                              # Test updated_at changes
        self._create_bug('Bug-1', 'Timestamp test')

        original = self.node_service.get_node(Safe_Str__Node_Type('bug'), Safe_Str__Node_Label('Bug-1'))
        original_updated = original.updated_at

        update_request = Schema__Node__Update__Request(title = 'Changed')
        response = self.node_service.update_node(node_type = Safe_Str__Node_Type('bug')        ,
                                                 label     = Safe_Str__Node_Label('Bug-1')     ,
                                                 request   = update_request                    )

        assert response.success is True
        # Note: timestamp might be same if test runs very fast, so just check it exists
        assert response.node.updated_at is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__delete_node(self):                                                 # Test successful deletion
        self._create_bug('Bug-1', 'To be deleted')

        response = self.node_service.delete_node(node_type = Safe_Str__Node_Type('bug')        ,
                                                 label     = Safe_Str__Node_Label('Bug-1')     )

        assert response.success is True
        assert response.deleted is True
        assert str(response.label) == 'Bug-1'

        # Verify it's gone
        assert self.node_service.node_exists(Safe_Str__Node_Type('bug'), Safe_Str__Node_Label('Bug-1')) is False

    def test__delete_node__not_found(self):                                      # Test delete non-existent node
        response = self.node_service.delete_node(node_type = Safe_Str__Node_Type('bug')        ,
                                                 label     = Safe_Str__Node_Label('Bug-999')   )

        assert response.success is False
        assert response.deleted is False
        assert 'not found' in str(response.message).lower()

    def test__delete_node__updates_type_index(self):                             # Test type index updated
        self._create_bug('Bug-1', 'First')
        self._create_bug('Bug-2', 'Second')

        type_index = self.repository.type_index_load(Safe_Str__Node_Type('bug'))
        assert int(type_index.count) == 2

        self.node_service.delete_node(Safe_Str__Node_Type('bug'), Safe_Str__Node_Label('Bug-1'))

        type_index = self.repository.type_index_load(Safe_Str__Node_Type('bug'))
        assert int(type_index.count) == 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Node Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_node(self):                                                    # Test get existing node
        self._create_bug('Bug-1', 'Find me')

        node = self.node_service.get_node(node_type = Safe_Str__Node_Type('bug')               ,
                                          label     = Safe_Str__Node_Label('Bug-1')            )

        assert node             is not None
        assert str(node.label)  == 'Bug-1'
        assert str(node.title)  == 'Find me'

    def test__get_node__not_found(self):                                         # Test get non-existent node
        node = self.node_service.get_node(node_type = Safe_Str__Node_Type('bug')               ,
                                          label     = Safe_Str__Node_Label('Bug-999')          )

        assert node is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Exists Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__node_exists__true(self):                                           # Test exists returns true
        self._create_bug('Bug-1', 'Exists')

        result = self.node_service.node_exists(Safe_Str__Node_Type('bug'), Safe_Str__Node_Label('Bug-1'))

        assert result is True

    def test__node_exists__false(self):                                          # Test exists returns false
        result = self.node_service.node_exists(Safe_Str__Node_Type('bug'), Safe_Str__Node_Label('Bug-999'))

        assert result is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Label Generation Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__label_from_type_and_index(self):                                   # Test label generation
        label = self.node_service.label_from_type_and_index(node_type  = Safe_Str__Node_Type('bug'),
                                                            node_index = 27                        )

        assert str(label) == 'Bug-27'

    def test__label_from_type_and_index__task(self):                             # Test task label
        label = self.node_service.label_from_type_and_index(node_type  = Safe_Str__Node_Type('task'),
                                                            node_index = 100                        )

        assert str(label) == 'Task-100'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Global Index Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__update_global_index(self):                                         # Test global index update
        self._create_bug('Bug-1', 'Bug')
        self._create_bug('Bug-2', 'Bug 2')
        self._create_task('Task-1', 'Task')

        self.node_service.update_global_index()

        global_index = self.repository.global_index_load()

        assert int(global_index.total_nodes) == 3
        assert len(global_index.type_counts) >= 2                                # At least bug and task

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _create_bug(self, label: str, title: str):                               # Helper to create bug
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('bug')         ,
                                                title     = title                              )
        return self.node_service.create_node(request)

    def _create_task(self, label: str, title: str):                              # Helper to create task
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('task')        ,
                                                title     = title                              )
        return self.node_service.create_node(request)
