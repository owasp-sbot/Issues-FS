# ═══════════════════════════════════════════════════════════════════════════════
# test_Link__Service - Unit tests for link service business logic
# Tests bidirectional link creation, deletion, and validation
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                               import TestCase
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.utils.Objects                                                                              import base_classes
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Safe_Str__Graph_Types                         import Safe_Str__Link_Verb, Safe_Str__Node_Type, Safe_Str__Node_Label
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Link__Create__Request                 import Schema__Link__Create__Request
from mgraph_ai_ui_html_transformation_workbench.schemas.graph.Schema__Node__Create__Request                 import Schema__Node__Create__Request
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Graph__Repository__Factory    import Graph__Repository__Factory
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Link__Service                 import Link__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Node__Service                 import Node__Service
from mgraph_ai_ui_html_transformation_workbench.service.issues.graph_services.Type__Service                 import Type__Service


class test_Link__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Shared setup - create once
        cls.repository    = Graph__Repository__Factory.create_memory()
        cls.type_service  = Type__Service(repository=cls.repository)
        cls.node_service  = Node__Service(repository=cls.repository)
        cls.link_service  = Link__Service(repository=cls.repository)

    def setUp(self):                                                             # Reset before each test
        self.repository.clear_storage()
        self.type_service.initialize_default_types()                             # Set up default types

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test service initialization
        with self.link_service as _:
            assert type(_)            is Link__Service
            assert base_classes(_)    == [Type_Safe, object]
            assert _.repository       is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Link Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__create_link(self):                                                 # Test successful link creation
        self._create_bug('Bug-1')
        self._create_task('Task-1')

        request = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('blocks')       ,
                                                target_label = Safe_Str__Node_Label('Task-1')      )

        response = self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')         ,
                                                 source_label = Safe_Str__Node_Label('Bug-1')      ,
                                                 request      = request                            )

        assert response.success      is True
        assert response.source_link  is not None
        assert response.target_link  is not None

    def test__create_link__bidirectional(self):                                  # Test both ends have links
        self._create_bug('Bug-1')
        self._create_task('Task-1')

        request = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('blocks')       ,
                                                target_label = Safe_Str__Node_Label('Task-1')      )

        self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')                    ,
                                      source_label = Safe_Str__Node_Label('Bug-1')                 ,
                                      request      = request                                       )

        # Check source node has forward link
        source = self.node_service.get_node(Safe_Str__Node_Type('bug'), Safe_Str__Node_Label('Bug-1'))
        assert len(source.links) == 1
        assert str(source.links[0].verb)         == 'blocks'
        assert str(source.links[0].target_label) == 'Task-1'

        # Check target node has inverse link
        target = self.node_service.get_node(Safe_Str__Node_Type('task'), Safe_Str__Node_Label('Task-1'))
        assert len(target.links) == 1
        assert str(target.links[0].verb)         == 'blocked-by'
        assert str(target.links[0].target_label) == 'Bug-1'

    def test__create_link__has_task(self):                                       # Test has-task link type
        self._create_feature('Feature-1')
        self._create_task('Task-1')

        request = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('has-task')     ,
                                                target_label = Safe_Str__Node_Label('Task-1')      )

        response = self.link_service.create_link(source_type  = Safe_Str__Node_Type('feature')     ,
                                                 source_label = Safe_Str__Node_Label('Feature-1')  ,
                                                 request      = request                            )

        assert response.success is True
        assert str(response.source_link.verb) == 'has-task'
        assert str(response.target_link.verb) == 'task-of'

    def test__create_link__assigned_to(self):                                    # Test assigned-to link type
        self._create_task('Task-1')
        self._create_person('Person-1')

        request = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('assigned-to')  ,
                                                target_label = Safe_Str__Node_Label('Person-1')    )

        response = self.link_service.create_link(source_type  = Safe_Str__Node_Type('task')        ,
                                                 source_label = Safe_Str__Node_Label('Task-1')     ,
                                                 request      = request                            )

        assert response.success is True
        assert str(response.source_link.verb) == 'assigned-to'
        assert str(response.target_link.verb) == 'assignee-of'

    def test__create_link__source_not_found(self):                               # Test source not found
        self._create_task('Task-1')

        request = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('blocks')       ,
                                                target_label = Safe_Str__Node_Label('Task-1')      )

        response = self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')         ,
                                                 source_label = Safe_Str__Node_Label('Bug-999')    ,  # Does not exist
                                                 request      = request                            )

        assert response.success is False
        assert 'not found' in str(response.message).lower()

    def test__create_link__target_not_found(self):                               # Test target not found
        self._create_bug('Bug-1')

        request = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('blocks')       ,
                                                target_label = Safe_Str__Node_Label('Task-999')    )  # Does not exist

        response = self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')         ,
                                                 source_label = Safe_Str__Node_Label('Bug-1')      ,
                                                 request      = request                            )

        assert response.success is False
        assert 'not found' in str(response.message).lower()

    def test__create_link__unknown_verb(self):                                   # Test unknown link type
        self._create_bug('Bug-1')
        self._create_task('Task-1')

        request = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('unknown-verb') ,
                                                target_label = Safe_Str__Node_Label('Task-1')      )

        response = self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')         ,
                                                 source_label = Safe_Str__Node_Label('Bug-1')      ,
                                                 request      = request                            )

        assert response.success is False
        assert 'Unknown link type' in str(response.message)

    def test__create_link__duplicate_link(self):                                 # Test duplicate link rejected
        self._create_bug('Bug-1')
        self._create_task('Task-1')

        request = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('blocks')       ,
                                                target_label = Safe_Str__Node_Label('Task-1')      )

        # First link succeeds
        response1 = self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')        ,
                                                  source_label = Safe_Str__Node_Label('Bug-1')     ,
                                                  request      = request                           )
        assert response1.success is True

        # Second identical link fails
        response2 = self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')        ,
                                                  source_label = Safe_Str__Node_Label('Bug-1')     ,
                                                  request      = request                           )
        assert response2.success is False
        assert 'already exists' in str(response2.message).lower()

    def test__create_link__multiple_links_same_source(self):                     # Test multiple links from same node
        self._create_bug('Bug-1')
        self._create_task('Task-1')
        self._create_task('Task-2')

        request1 = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('blocks')      ,
                                                 target_label = Safe_Str__Node_Label('Task-1')     )
        request2 = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('blocks')      ,
                                                 target_label = Safe_Str__Node_Label('Task-2')     )

        response1 = self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')        ,
                                                  source_label = Safe_Str__Node_Label('Bug-1')     ,
                                                  request      = request1                          )
        response2 = self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')        ,
                                                  source_label = Safe_Str__Node_Label('Bug-1')     ,
                                                  request      = request2                          )

        assert response1.success is True
        assert response2.success is True

        # Check source has both links
        source = self.node_service.get_node(Safe_Str__Node_Type('bug'), Safe_Str__Node_Label('Bug-1'))
        assert len(source.links) == 2

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Link Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__delete_link(self):                                                 # Test successful link deletion
        self._create_bug('Bug-1')
        self._create_task('Task-1')
        self._create_link_blocks('Bug-1', 'Task-1')

        response = self.link_service.delete_link(source_type  = Safe_Str__Node_Type('bug')         ,
                                                 source_label = Safe_Str__Node_Label('Bug-1')      ,
                                                 target_label = Safe_Str__Node_Label('Task-1')     )

        assert response.success is True
        assert response.deleted is True

    def test__delete_link__removes_both_directions(self):                        # Test both ends cleaned
        self._create_bug('Bug-1')
        self._create_task('Task-1')
        self._create_link_blocks('Bug-1', 'Task-1')

        self.link_service.delete_link(source_type  = Safe_Str__Node_Type('bug')                    ,
                                      source_label = Safe_Str__Node_Label('Bug-1')                 ,
                                      target_label = Safe_Str__Node_Label('Task-1')                )

        # Check source has no links
        source = self.node_service.get_node(Safe_Str__Node_Type('bug'), Safe_Str__Node_Label('Bug-1'))
        assert len(source.links) == 0

        # Check target has no links
        target = self.node_service.get_node(Safe_Str__Node_Type('task'), Safe_Str__Node_Label('Task-1'))
        assert len(target.links) == 0

    def test__delete_link__source_not_found(self):                               # Test delete from non-existent source
        response = self.link_service.delete_link(source_type  = Safe_Str__Node_Type('bug')         ,
                                                 source_label = Safe_Str__Node_Label('Bug-999')    ,
                                                 target_label = Safe_Str__Node_Label('Task-1')     )

        assert response.success is False
        assert response.deleted is False

    def test__delete_link__link_not_found(self):                                 # Test delete non-existent link
        self._create_bug('Bug-1')
        self._create_task('Task-1')
        # No link created

        response = self.link_service.delete_link(source_type  = Safe_Str__Node_Type('bug')         ,
                                                 source_label = Safe_Str__Node_Label('Bug-1')      ,
                                                 target_label = Safe_Str__Node_Label('Task-1')     )

        assert response.success is False
        assert response.deleted is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Links Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list_links(self):                                                  # Test list links for node
        self._create_bug('Bug-1')
        self._create_task('Task-1')
        self._create_task('Task-2')
        self._create_link_blocks('Bug-1', 'Task-1')
        self._create_link_blocks('Bug-1', 'Task-2')

        response = self.link_service.list_links(node_type = Safe_Str__Node_Type('bug')             ,
                                                label     = Safe_Str__Node_Label('Bug-1')          )

        assert response.success is True
        assert len(response.links) == 2

    def test__list_links__empty(self):                                           # Test list links when none
        self._create_bug('Bug-1')

        response = self.link_service.list_links(node_type = Safe_Str__Node_Type('bug')             ,
                                                label     = Safe_Str__Node_Label('Bug-1')          )

        assert response.success is True
        assert len(response.links) == 0

    def test__list_links__node_not_found(self):                                  # Test list links for non-existent
        response = self.link_service.list_links(node_type = Safe_Str__Node_Type('bug')             ,
                                                label     = Safe_Str__Node_Label('Bug-999')        )

        assert response.success is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__find_link_type(self):                                              # Test finding link type
        link_type = self.link_service.find_link_type(Safe_Str__Link_Verb('blocks'))

        assert link_type              is not None
        assert str(link_type.verb)    == 'blocks'
        assert str(link_type.inverse_verb) == 'blocked-by'

    def test__find_link_type__not_found(self):                                   # Test link type not found
        link_type = self.link_service.find_link_type(Safe_Str__Link_Verb('nonexistent'))

        assert link_type is None

    def test__parse_label(self):                                                 # Test label parsing
        node_type, label = self.link_service.parse_label(Safe_Str__Node_Label('Bug-27'))

        assert str(node_type) == 'bug'
        assert str(label)     == 'Bug-27'

    def test__parse_label__task(self):                                           # Test task label parsing
        node_type, label = self.link_service.parse_label(Safe_Str__Node_Label('Task-100'))

        assert str(node_type) == 'task'
        assert str(label)     == 'Task-100'

    def test__parse_label__feature(self):                                        # Test feature label parsing
        node_type, label = self.link_service.parse_label(Safe_Str__Node_Label('Feature-5'))

        assert str(node_type) == 'feature'
        assert str(label)     == 'Feature-5'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def _create_bug(self, label: str):                                           # Helper to create bug
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('bug')             ,
                                                title     = f'Test {label}'                        )
        return self.node_service.create_node(request)

    def _create_task(self, label: str):                                          # Helper to create task
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('task')            ,
                                                title     = f'Test {label}'                        )
        return self.node_service.create_node(request)

    def _create_feature(self, label: str):                                       # Helper to create feature
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('feature')         ,
                                                title     = f'Test {label}'                        )
        return self.node_service.create_node(request)

    def _create_person(self, label: str):                                        # Helper to create person
        request = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type('person')          ,
                                                title     = f'Test {label}'                        )
        return self.node_service.create_node(request)

    def _create_link_blocks(self, source_label: str, target_label: str):         # Helper to create blocks link
        request = Schema__Link__Create__Request(verb         = Safe_Str__Link_Verb('blocks')       ,
                                                target_label = Safe_Str__Node_Label(target_label)  )
        return self.link_service.create_link(source_type  = Safe_Str__Node_Type('bug')             ,
                                             source_label = Safe_Str__Node_Label(source_label)     ,
                                             request      = request                                )
