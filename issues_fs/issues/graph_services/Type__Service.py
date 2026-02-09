# ═══════════════════════════════════════════════════════════════════════════════
# Type__Service - Business logic for type definitions
# Manages node types (bug, task, feature) and link types (blocks, has-task)
# Phase 1: Added git-repo type for root issue support
# Phase 2: B15 (update_node_type), B16 (update_link_type)
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                                             import List, Optional
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                            import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                                        import Obj_Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe
from issues_fs.schemas.graph.Safe_Str__Graph_Types                                                      import Safe_Str__Node_Type, Safe_Str__Status, Safe_Str__Node_Type_Display, Safe_Str__Link_Verb
from issues_fs.schemas.graph.Schema__Node__Type                                                         import Schema__Node__Type
from issues_fs.schemas.graph.Schema__Node__Type__Update                                                 import Schema__Node__Type__Update
from issues_fs.schemas.graph.Schema__Node__Type__Update__Response                                       import Schema__Node__Type__Update__Response
from issues_fs.schemas.graph.Schema__Link__Type                                                         import Schema__Link__Type
from issues_fs.schemas.graph.Schema__Link__Type__Update                                                 import Schema__Link__Type__Update
from issues_fs.schemas.graph.Schema__Link__Type__Update__Response                                       import Schema__Link__Type__Update__Response
from issues_fs.schemas.safe_str.Safe_Str__Hex_Color                                                     import Safe_Str__Hex_Color
from issues_fs.issues.graph_services.Graph__Repository                                                  import Graph__Repository


class Type__Service(Type_Safe):                                                  # Type definition service
    repository : Graph__Repository                                               # Data access layer

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Type Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def list_node_types(self) -> List[Schema__Node__Type]:                       # Get all node types
        return self.repository.node_types_load()

    def get_node_type(self                         ,                             # Get single node type
                      name : Safe_Str__Node_Type
                 ) -> Schema__Node__Type:
        types = self.repository.node_types_load()
        for t in types:
            if str(t.name) == str(name):
                return t
        return None

    @type_safe
    def create_node_type(self                                                       ,                  # Create new node type
                         name           : Safe_Str__Node_Type                       ,
                         display_name   : Safe_Str__Node_Type_Display               ,
                         description    : Safe_Str__Text                 = ''       ,
                         color          : Safe_Str__Hex_Color            = '#888888',
                         statuses       : List[str]                      = None     ,
                         default_status : Safe_Str__Status               = 'backlog'
                    ) -> Schema__Node__Type:
        types = self.repository.node_types_load()

        for t in types:
            if t.name == name:
                return None                                                      # Already exists

        status_list = statuses or ['backlog', 'in-progress', 'done']

        node_type = Schema__Node__Type(type_id        = Obj_Id()       ,
                                       name           = name           ,
                                       display_name   = display_name   ,
                                       description    = description    ,
                                       color          = color          ,
                                       statuses       = status_list    ,
                                       default_status = default_status )

        types.append(node_type)
        self.repository.node_types_save(types)
        return node_type

    def delete_node_type(self                         ,                          # Delete node type
                         name : Safe_Str__Node_Type
                    ) -> bool:
        types = self.repository.node_types_load()

        type_index = self.repository.type_index_load(name)                       # Check if any nodes of this type exist
        if int(type_index.count) > 0:
            return False                                                         # Cannot delete type with existing nodes

        types = [t for t in types if str(t.name) != str(name)]                   # Remove type
        self.repository.node_types_save(types)
        return True

    @type_safe
    def update_node_type(self                                     ,              # Phase 2 (B15): Update node type
                         name    : Safe_Str__Node_Type            ,
                         updates : Schema__Node__Type__Update
                    ) -> Schema__Node__Type__Update__Response:
        types      = self.repository.node_types_load()
        found_type = None
        found_idx  = -1

        for idx, t in enumerate(types):                                          # Find the type to update
            if str(t.name) == str(name):
                found_type = t
                found_idx  = idx
                break

        if found_type is None:                                                   # Type not found
            return Schema__Node__Type__Update__Response(success = False                            ,
                                                         message = f'Node type not found: {name}' )

        if updates.display_name is not None and str(updates.display_name) != '':  # Apply partial updates
            found_type.display_name = updates.display_name
        if updates.description is not None and str(updates.description) != '':
            found_type.description = updates.description
        if updates.icon is not None and str(updates.icon) != '':
            found_type.icon = updates.icon
        if updates.color is not None and str(updates.color) != '':
            found_type.color = updates.color
        if updates.statuses is not None:
            found_type.statuses = updates.statuses
        if updates.default_status is not None and str(updates.default_status) != '':
            found_type.default_status = updates.default_status

        types[found_idx] = found_type                                            # Replace in list
        self.repository.node_types_save(types)                                   # Persist changes

        return Schema__Node__Type__Update__Response(success   = True       ,
                                                     node_type = found_type ,
                                                     message   = f'Node type updated: {name}')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Link Type Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    @type_safe
    def list_link_types(self) -> List[Schema__Link__Type]:                       # Get all link types
        return self.repository.link_types_load()

    def get_link_type(self                         ,                             # Get link type by verb
                      verb : Safe_Str__Link_Verb
                 ) -> Optional[Schema__Link__Type]:
        types = self.repository.link_types_load()
        for t in types:
            if str(t.verb) == str(verb):
                return t
        return None

    @type_safe
    def create_link_type(self                                 ,                  # Create new link type
                         verb          : Safe_Str__Link_Verb  ,
                         inverse_verb  : Safe_Str__Link_Verb                  ,
                         description   : Safe_Str__Text             = ''      ,
                         source_types  : List[Safe_Str__Node_Type]  = None    ,
                         target_types  : List[Safe_Str__Node_Type]  = None
                    ) -> Schema__Link__Type:
        types = self.repository.link_types_load()

        for t in types:
            if str(t.verb) == str(verb):
                return None                                                      # Already exists

        link_type = Schema__Link__Type(link_type_id = Obj_Id()      ,
                                       verb         = verb          ,
                                       inverse_verb = inverse_verb  ,
                                       description  = description   ,
                                       source_types = source_types  ,
                                       target_types = target_types  )

        types.append(link_type)
        self.repository.link_types_save(types)
        return link_type

    @type_safe
    def update_link_type(self                                     ,              # Phase 2 (B16): Update link type
                         verb    : Safe_Str__Link_Verb            ,
                         updates : Schema__Link__Type__Update
                    ) -> Schema__Link__Type__Update__Response:
        types      = self.repository.link_types_load()
        found_type = None
        found_idx  = -1

        for idx, t in enumerate(types):                                          # Find the link type to update
            if str(t.verb) == str(verb):
                found_type = t
                found_idx  = idx
                break

        if found_type is None:                                                   # Link type not found
            return Schema__Link__Type__Update__Response(success = False                            ,
                                                         message = f'Link type not found: {verb}' )

        if updates.inverse_verb is not None and str(updates.inverse_verb) != '':  # Apply partial updates
            found_type.inverse_verb = updates.inverse_verb
        if updates.description is not None and str(updates.description) != '':
            found_type.description = updates.description
        if updates.source_types is not None:
            found_type.source_types = updates.source_types
        if updates.target_types is not None:
            found_type.target_types = updates.target_types

        types[found_idx] = found_type                                            # Replace in list
        self.repository.link_types_save(types)                                   # Persist changes

        return Schema__Link__Type__Update__Response(success   = True       ,
                                                     link_type = found_type ,
                                                     message   = f'Link type updated: {verb}')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Default Type Initialization
    # ═══════════════════════════════════════════════════════════════════════════════

    def initialize_default_types(self) -> None:                                  # Set up default types
        if len(self.repository.node_types_load()) > 0:                           # Check if already initialized
            return

        # ───────────────────────────────────────────────────────────────────────────
        # Node Types
        # ───────────────────────────────────────────────────────────────────────────

        self.create_node_type(name           = Safe_Str__Node_Type('git-repo')     ,  # NEW: Root issue type for git repositories
                              display_name   = 'GitRepo'                           ,
                              description    = 'Git repository root - contains all issues',
                              color          = '#6366f1'                           ,  # Indigo color
                              statuses       = ['active', 'archived']              ,
                              default_status = 'active'                            )

        self.create_node_type(name           = Safe_Str__Node_Type('bug')          ,
                              display_name   = 'Bug'                               ,
                              description    = 'Defect or error in the system'     ,
                              color          = '#ef4444'                           ,
                              statuses       = ['backlog', 'confirmed', 'in-progress', 'testing', 'resolved', 'closed'],
                              default_status = 'backlog'                           )

        self.create_node_type(name           = Safe_Str__Node_Type('task')         ,
                              display_name   = 'Task'                              ,
                              description    = 'Unit of work to be completed'      ,
                              color          = '#3b82f6'                           ,
                              statuses       = ['backlog', 'todo', 'in-progress', 'review', 'done'],
                              default_status = 'backlog'                           )

        self.create_node_type(name           = Safe_Str__Node_Type('feature')      ,
                              display_name   = 'Feature'                           ,
                              description    = 'High-level capability'             ,
                              color          = '#22c55e'                           ,
                              statuses       = ['proposed', 'approved', 'in-progress', 'released'],
                              default_status = 'proposed'                          )

        self.create_node_type(name           = Safe_Str__Node_Type('person')       ,
                              display_name   = 'Person'                            ,
                              description    = 'Human or agent identity'           ,
                              color          = '#8b5cf6'                           ,
                              statuses       = ['active', 'inactive']              ,
                              default_status = 'active'                            )

        # ───────────────────────────────────────────────────────────────────────────
        # Link Types
        # ───────────────────────────────────────────────────────────────────────────

        self.create_link_type(verb         = Safe_Str__Link_Verb('blocks')          ,
                              inverse_verb = 'blocked-by'                           ,
                              description  = 'Prevents progress on target'          ,
                              source_types = ['bug', 'task']                        ,
                              target_types = ['task', 'feature']                    )

        self.create_link_type(verb         = Safe_Str__Link_Verb('has-task')        ,
                              inverse_verb = 'task-of'                              ,
                              description  = 'Contains as sub-work'                 ,
                              source_types = ['feature', 'git-repo']                ,  # git-repo can have tasks
                              target_types = ['task']                               )

        self.create_link_type(verb         = Safe_Str__Link_Verb('assigned-to')     ,
                              inverse_verb = 'assignee-of'                          ,
                              description  = 'Work assigned to person/agent'        ,
                              source_types = ['bug', 'task', 'feature']             ,
                              target_types = ['person']                             )

        self.create_link_type(verb         = Safe_Str__Link_Verb('depends-on')      ,
                              inverse_verb = 'dependency-of'                        ,
                              description  = 'Requires target to complete first'    ,
                              source_types = ['task', 'feature']                    ,
                              target_types = ['task', 'feature']                    )

        self.create_link_type(verb         = Safe_Str__Link_Verb('relates-to')      ,
                              inverse_verb = 'relates-to'                           ,
                              description  = 'General association (symmetric)'      ,
                              source_types = ['bug', 'task', 'feature', 'git-repo'] ,
                              target_types = ['bug', 'task', 'feature', 'git-repo'] )

        self.create_link_type(verb         = Safe_Str__Link_Verb('contains')        ,  # NEW: For hierarchical structure
                              inverse_verb = 'contained-by'                         ,
                              description  = 'Parent contains child issue'          ,
                              source_types = ['git-repo', 'feature', 'task']        ,
                              target_types = ['bug', 'task', 'feature']             )