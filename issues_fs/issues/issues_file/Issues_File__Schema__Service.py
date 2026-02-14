# ═══════════════════════════════════════════════════════════════════════════════
# Issues_File__Schema__Service - Type auto-detection and schema validation
# Validates that labels and statuses in .issues files conform to predefined
# type schemas (Task, Bug, Workstream, Feature, Question, etc.)
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Dict, List, Tuple
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from issues_fs.issues.issues_file.Issues_File__Loader__Service                  import Issues_File__Loader__Service


class Schema__Issues_Type__Definition(Type_Safe):
    name            : str                                                       # type name, e.g. "task"
    display_name    : str                                                       # e.g. "Task"
    valid_statuses  : List[str]                                                 # allowed status values
    description     : str                                                       # what this type represents


class Schema__Issues_Schema__Error(Type_Safe):
    label      : str                                                            # which issue
    field      : str                                                            # "status" or "type"
    message    : str                                                            # what's wrong
    source     : str                                                            # which file


class Schema__Issues_Schema__Summary(Type_Safe):
    total_checked    : int
    total_errors     : int
    errors           : List[Schema__Issues_Schema__Error]
    unknown_types    : List[str]                                                # types with no schema
    is_valid         : bool


PREDEFINED_SCHEMAS = {
    'task'          : Schema__Issues_Type__Definition(
                          name           = 'task'                                                            ,
                          display_name   = 'Task'                                                            ,
                          valid_statuses = ['backlog', 'todo', 'in-progress', 'review', 'done']              ,
                          description    = 'Unit of work to be completed'                                    ),
    'bug'           : Schema__Issues_Type__Definition(
                          name           = 'bug'                                                             ,
                          display_name   = 'Bug'                                                             ,
                          valid_statuses = ['backlog', 'confirmed', 'in-progress', 'testing', 'resolved', 'closed'],
                          description    = 'Defect or error in the system'                                   ),
    'workstream'    : Schema__Issues_Type__Definition(
                          name           = 'workstream'                                                      ,
                          display_name   = 'Workstream'                                                      ,
                          valid_statuses = ['todo', 'in-progress', 'done', 'blocked']                        ,
                          description    = 'High-level work stream grouping tasks'                           ),
    'feature'       : Schema__Issues_Type__Definition(
                          name           = 'feature'                                                         ,
                          display_name   = 'Feature'                                                         ,
                          valid_statuses = ['proposed', 'approved', 'in-progress', 'released']               ,
                          description    = 'High-level capability'                                           ),
    'question'      : Schema__Issues_Type__Definition(
                          name           = 'question'                                                        ,
                          display_name   = 'Question'                                                        ,
                          valid_statuses = ['open', 'answered', 'closed']                                    ,
                          description    = 'Question or decision to be resolved'                             ),
    'risk'          : Schema__Issues_Type__Definition(
                          name           = 'risk'                                                            ,
                          display_name   = 'Risk'                                                            ,
                          valid_statuses = ['identified', 'mitigated', 'accepted', 'closed']                 ,
                          description    = 'Risk or concern to be tracked'                                   ),
    'user-journey'  : Schema__Issues_Type__Definition(
                          name           = 'user-journey'                                                    ,
                          display_name   = 'User Journey'                                                    ,
                          valid_statuses = ['draft', 'in-progress', 'done']                                  ,
                          description    = 'End-to-end user flow or scenario'                                ),
}


class Issues_File__Schema__Service(Type_Safe):
    loader  : Issues_File__Loader__Service
    schemas : Dict[str, Schema__Issues_Type__Definition] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.schemas is None:
            self.schemas = dict(PREDEFINED_SCHEMAS)

    def check_content(self, content: str, source_file: str = ''
                     ) -> Schema__Issues_Schema__Summary:
        load_result  = self.loader.load_content(content, source_file)
        errors       = []
        unknown_types = set()

        for node in load_result.nodes:
            node_type = str(node.node_type)
            status    = str(node.status)
            label     = str(node.label)

            if node_type not in self.schemas:
                unknown_types.add(node_type)
                continue

            schema = self.schemas[node_type]
            if status not in schema.valid_statuses:
                errors.append(Schema__Issues_Schema__Error(
                    label   = label                                                ,
                    field   = 'status'                                             ,
                    message = f"Invalid status '{status}' for type '{node_type}'. "
                              f"Valid: {', '.join(schema.valid_statuses)}"         ,
                    source  = source_file                                          ))

        return Schema__Issues_Schema__Summary(
            total_checked  = len(load_result.nodes)      ,
            total_errors   = len(errors)                 ,
            errors         = errors                      ,
            unknown_types  = sorted(unknown_types)       ,
            is_valid       = len(errors) == 0            )

    def check_multiple(self, files: List[Tuple[str, str]]
                      ) -> Schema__Issues_Schema__Summary:
        all_errors      = []
        all_unknown      = set()
        total_checked   = 0

        for content, source_file in files:
            summary = self.check_content(content, source_file)
            all_errors.extend(summary.errors)
            all_unknown.update(summary.unknown_types)
            total_checked += summary.total_checked

        return Schema__Issues_Schema__Summary(
            total_checked  = total_checked             ,
            total_errors   = len(all_errors)           ,
            errors         = all_errors                ,
            unknown_types  = sorted(all_unknown)       ,
            is_valid       = len(all_errors) == 0      )

    def get_schema(self, type_name: str) -> Schema__Issues_Type__Definition:
        return self.schemas.get(type_name)

    def list_schemas(self) -> List[Schema__Issues_Type__Definition]:
        return list(self.schemas.values())

    def register_schema(self, schema: Schema__Issues_Type__Definition) -> None:
        self.schemas[schema.name] = schema

    def format_report(self, summary: Schema__Issues_Schema__Summary) -> str:
        lines = []

        if summary.is_valid:
            lines.append(f'Schema Check: PASS')
        else:
            lines.append(f'Schema Check: FAIL')

        lines.append(f'Issues checked: {summary.total_checked}')
        lines.append(f'Schema errors:  {summary.total_errors}')

        if summary.unknown_types:
            lines.append(f'Unknown types:  {", ".join(summary.unknown_types)}')

        if summary.errors:
            lines.append('')
            lines.append('Errors:')
            for error in summary.errors:
                lines.append(f'  {error.label}: {error.message}')

        return '\n'.join(lines)
