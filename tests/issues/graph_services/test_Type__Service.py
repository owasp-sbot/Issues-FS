# ═══════════════════════════════════════════════════════════════════════════════
# test_Type__Service - Unit tests for type definition service
# Tests node type and link type management operations
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                            import TestCase
from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.utils.Objects                                                                           import base_classes
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types                      import Safe_Str__Node_Type, Safe_Str__Link_Verb
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Create__Request              import Schema__Node__Create__Request
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository__Factory import Graph__Repository__Factory
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Node__Service              import Node__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Type__Service              import Type__Service


class test_Type__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup - create once
        cls.repository    = Graph__Repository__Factory.create_memory()
        cls.type_service  = Type__Service(repository=cls.repository)
        cls.node_service  = Node__Service(repository=cls.repository)

    def setUp(self):                                                             # Reset before each test
        self.repository.clear_storage()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test service initialization
        with self.type_service as _:
            assert type(_)            is Type__Service
            assert base_classes(_)    == [Type_Safe, object]
            assert _.repository       is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialize Default Types Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__initialize_default_types(self):                                    # Test default types creation
        self.type_service.initialize_default_types()

        node_types = self.type_service.list_node_types()
        link_types = self.type_service.list_link_types()

        assert len(node_types) >= 4                                              # bug, task, feature, person
        assert len(link_types) >= 5                                              # blocks, has-task, assigned-to, depends-on, relates-to

    def test__initialize_default_types__bug_type(self):                          # Test bug type created correctly
        self.type_service.initialize_default_types()

        bug_type = self.type_service.get_node_type(Safe_Str__Node_Type('bug'))

        assert bug_type                    is not None
        assert str(bug_type.name)          == 'bug'
        assert str(bug_type.display_name)  == 'Bug'
        assert str(bug_type.color)         == '#ef4444'
        assert 'backlog' in [str(s) for s in bug_type.statuses]

    def test__initialize_default_types__task_type(self):                         # Test task type created correctly
        self.type_service.initialize_default_types()

        task_type = self.type_service.get_node_type(Safe_Str__Node_Type('task'))

        assert task_type                    is not None
        assert str(task_type.name)          == 'task'
        assert str(task_type.display_name)  == 'Task'
        assert str(task_type.color)         == '#3b82f6'

    def test__initialize_default_types__feature_type(self):                      # Test feature type created correctly
        self.type_service.initialize_default_types()

        feature_type = self.type_service.get_node_type(Safe_Str__Node_Type('feature'))

        assert feature_type                    is not None
        assert str(feature_type.name)          == 'feature'
        assert str(feature_type.display_name)  == 'Feature'
        assert str(feature_type.color)         == '#22c55e'

    def test__initialize_default_types__person_type(self):                       # Test person type created correctly
        self.type_service.initialize_default_types()

        person_type = self.type_service.get_node_type(Safe_Str__Node_Type('person'))

        assert person_type                    is not None
        assert str(person_type.name)          == 'person'
        assert str(person_type.display_name)  == 'Person'
        assert str(person_type.color)         == '#8b5cf6'

    def test__initialize_default_types__blocks_link(self):                       # Test blocks link type
        self.type_service.initialize_default_types()

        blocks = self.type_service.get_link_type(Safe_Str__Link_Verb('blocks'))

        assert blocks                        is not None
        assert str(blocks.verb)              == 'blocks'
        assert str(blocks.inverse_verb)      == 'blocked-by'

    def test__initialize_default_types__idempotent(self):                        # Test calling twice is safe
        self.type_service.initialize_default_types()
        count1 = len(self.type_service.list_node_types())

        self.type_service.initialize_default_types()                             # Call again
        count2 = len(self.type_service.list_node_types())

        assert count1 == count2                                                  # No duplicates

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Node Types Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list_node_types__empty(self):                                      # Test list when empty
        types = self.type_service.list_node_types()

        assert types == []

    def test__list_node_types(self):                                             # Test list after init
        self.type_service.initialize_default_types()

        types = self.type_service.list_node_types()

        assert len(types) >= 4
        type_names = [str(t.name) for t in types]
        assert 'bug'     in type_names
        assert 'task'    in type_names
        assert 'feature' in type_names
        assert 'person'  in type_names

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Node Type Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_node_type(self):                                               # Test get existing type
        self.type_service.initialize_default_types()

        bug_type = self.type_service.get_node_type(Safe_Str__Node_Type('bug'))

        assert bug_type is not None
        assert str(bug_type.name) == 'bug'

    def test__get_node_type__not_found(self):                                    # Test get non-existent type
        self.type_service.initialize_default_types()

        result = self.type_service.get_node_type(Safe_Str__Node_Type('unknown'))

        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Node Type Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__create_node_type(self):                                            # Test create new type
        result = self.type_service.create_node_type(
            name           = Safe_Str__Node_Type('epic')                         ,
            display_name   = 'Epic'                                              ,
            description    = 'Large initiative spanning multiple features'       ,
            color          = '#a855f7'                                           ,
            statuses       = ['proposed', 'in-progress', 'done']                 ,
            default_status = 'proposed'
        )

        assert result                    is not None
        assert str(result.name)          == 'epic'
        assert str(result.display_name)  == 'Epic'
        assert str(result.color)         == '#a855f7'
        assert len(result.statuses)      == 3

    def test__create_node_type__with_defaults(self):                             # Test create with default values
        result = self.type_service.create_node_type(
            name         = Safe_Str__Node_Type('simple')                         ,
            display_name = 'Simple'
        )

        assert result                    is not None
        assert str(result.name)          == 'simple'
        assert str(result.color)         == '#888888'                            # Default color
        assert len(result.statuses)      >= 1                                    # Has default statuses

    def test__create_node_type__duplicate(self):                                 # Test create duplicate fails
        self.type_service.create_node_type(name=Safe_Str__Node_Type('custom'), display_name='Custom')

        result = self.type_service.create_node_type(name=Safe_Str__Node_Type('custom'), display_name='Custom Again')

        assert result is None                                                    # Duplicate rejected

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Node Type Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__delete_node_type(self):                                            # Test delete type
        self.type_service.create_node_type(name=Safe_Str__Node_Type('deleteme'), display_name='Delete Me')

        result = self.type_service.delete_node_type(Safe_Str__Node_Type('deleteme'))

        assert result is True

        # Verify deleted
        assert self.type_service.get_node_type(Safe_Str__Node_Type('deleteme')) is None

    def test__delete_node_type__not_found(self):                                 # Test delete non-existent
        result = self.type_service.delete_node_type(Safe_Str__Node_Type('nonexistent'))

        # Should be False or silently succeed (type didn't exist)
        # Implementation returns False if types list doesn't change

    def test__delete_node_type__with_existing_nodes(self):                       # Test cannot delete type with nodes
        self.type_service.initialize_default_types()

        # Create a node of type 'bug'
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('bug')             ,
                                                title     = 'Existing bug'                         )
        self.node_service.create_node(request)

        # Try to delete 'bug' type
        result = self.type_service.delete_node_type(Safe_Str__Node_Type('bug'))

        assert result is False                                                   # Cannot delete type with nodes

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Link Types Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list_link_types__empty(self):                                      # Test list when empty
        types = self.type_service.list_link_types()

        assert types == []

    def test__list_link_types(self):                                             # Test list after init
        self.type_service.initialize_default_types()

        types = self.type_service.list_link_types()

        assert len(types) >= 5
        verbs = [str(t.verb) for t in types]
        assert 'blocks'      in verbs
        assert 'has-task'    in verbs
        assert 'assigned-to' in verbs

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Link Type Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_link_type(self):                                               # Test get existing link type
        self.type_service.initialize_default_types()

        blocks = self.type_service.get_link_type(Safe_Str__Link_Verb('blocks'))

        assert blocks                   is not None
        assert str(blocks.verb)         == 'blocks'
        assert str(blocks.inverse_verb) == 'blocked-by'

    def test__get_link_type__not_found(self):                                    # Test get non-existent link type
        self.type_service.initialize_default_types()

        result = self.type_service.get_link_type(Safe_Str__Link_Verb('unknown'))

        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Link Type Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__create_link_type(self):                                            # Test create new link type
        result = self.type_service.create_link_type(
            verb         = Safe_Str__Link_Verb('parent-of')                      ,
            inverse_verb = 'child-of'                                            ,
            description  = 'Parent-child relationship'                           ,
            source_types = ['feature']                                           ,
            target_types = ['feature']
        )

        assert result                        is not None
        assert str(result.verb)              == 'parent-of'
        assert str(result.inverse_verb)      == 'child-of'

    def test__create_link_type__duplicate(self):                                 # Test create duplicate fails
        self.type_service.create_link_type(verb=Safe_Str__Link_Verb('custom-link'), inverse_verb='custom-link-inverse')

        result = self.type_service.create_link_type(verb=Safe_Str__Link_Verb('custom-link'), inverse_verb='another')

        assert result is None                                                    # Duplicate rejected

    # ═══════════════════════════════════════════════════════════════════════════════
    # Default Type Configuration Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__default_types__bug_statuses(self):                                 # Test bug has correct statuses
        self.type_service.initialize_default_types()

        bug_type = self.type_service.get_node_type(Safe_Str__Node_Type('bug'))
        statuses = [str(s) for s in bug_type.statuses]

        assert 'backlog'     in statuses
        assert 'confirmed'   in statuses
        assert 'in-progress' in statuses
        assert 'testing'     in statuses
        assert 'resolved'    in statuses
        assert 'closed'      in statuses

    def test__default_types__task_statuses(self):                                # Test task has correct statuses
        self.type_service.initialize_default_types()

        task_type = self.type_service.get_node_type(Safe_Str__Node_Type('task'))
        statuses = [str(s) for s in task_type.statuses]

        assert 'backlog'     in statuses
        assert 'todo'        in statuses
        assert 'in-progress' in statuses
        assert 'review'      in statuses
        assert 'done'        in statuses

    def test__default_types__feature_statuses(self):                             # Test feature has correct statuses
        self.type_service.initialize_default_types()

        feature_type = self.type_service.get_node_type(Safe_Str__Node_Type('feature'))
        statuses = [str(s) for s in feature_type.statuses]

        assert 'proposed'    in statuses
        assert 'approved'    in statuses
        assert 'in-progress' in statuses
        assert 'released'    in statuses

    def test__default_types__blocks_source_types(self):                          # Test blocks source constraints
        self.type_service.initialize_default_types()

        blocks = self.type_service.get_link_type(Safe_Str__Link_Verb('blocks'))
        source_types = [str(t) for t in blocks.source_types]

        assert 'bug'  in source_types
        assert 'task' in source_types

    def test__default_types__blocks_target_types(self):                          # Test blocks target constraints
        self.type_service.initialize_default_types()

        blocks = self.type_service.get_link_type(Safe_Str__Link_Verb('blocks'))
        target_types = [str(t) for t in blocks.target_types]

        assert 'task'    in target_types
        assert 'feature' in target_types
