#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
# Migration Script: Convert all node.json → issue.json
# Phase 2 (B13): Run this BEFORE deploying B13 changes
#
# Usage:
#   python -m scripts.migrate_node_to_issue_json --path /path/to/.issues
#   python -m scripts.migrate_node_to_issue_json --path /path/to/.issues --dry-run
# ═══════════════════════════════════════════════════════════════════════════════

import argparse
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe


class Migration__Node_To_Issue_Json(Type_Safe):                                  # Migration runner
    storage_fs : object                                                          # Storage filesystem

    @type_safe
    def run(self) -> dict:                                                       # Execute migration
        all_paths = self.storage_fs.files__paths()
        results   = {'converted': 0, 'deleted': 0, 'skipped': 0, 'errors': []}

        for path in all_paths:
            if path.endswith('/node.json') is False:
                continue

            issue_path = path.replace('/node.json', '/issue.json')

            try:
                if self.storage_fs.file__exists(issue_path) is True:
                    # issue.json already exists, just delete node.json
                    self.storage_fs.file__delete(path)
                    results['deleted'] += 1
                else:
                    # Copy node.json → issue.json, then delete node.json
                    content = self.storage_fs.file__bytes(path)
                    self.storage_fs.file__save(issue_path, content)
                    self.storage_fs.file__delete(path)
                    results['converted'] += 1
            except Exception as e:
                results['errors'].append(f'{path}: {str(e)}')

        return results

    @type_safe
    def dry_run(self) -> dict:                                                   # Preview migration
        all_paths = self.storage_fs.files__paths()
        results   = {'to_convert': [], 'to_delete': []}

        for path in all_paths:
            if path.endswith('/node.json') is False:
                continue

            issue_path = path.replace('/node.json', '/issue.json')

            if self.storage_fs.file__exists(issue_path) is True:
                results['to_delete'].append(path)
            else:
                results['to_convert'].append(path)

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Migrate node.json files to issue.json',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Preview what would be migrated
  python -m scripts.migrate_node_to_issue_json --path .issues --dry-run

  # Run the actual migration
  python -m scripts.migrate_node_to_issue_json --path .issues
        '''
    )
    parser.add_argument('--path', required=True, help='Path to .issues folder')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    # Import here to avoid circular imports
    from memory_fs.Memory_FS import Memory_FS
    from memory_fs.storage_fs.providers.Storage_FS__Local_Disk import Storage_FS__Local_Disk

    print(f'Scanning: {args.path}')

    storage_fs = Storage_FS__Local_Disk(root_path=args.path)
    migration  = Migration__Node_To_Issue_Json(storage_fs=storage_fs)

    if args.dry_run:
        results = migration.dry_run()
        print(f'\nDry run results:')
        print(f'  Files to convert: {len(results["to_convert"])}')
        for path in results['to_convert']:
            print(f'    → {path}')
        print(f'  Files to delete (issue.json exists): {len(results["to_delete"])}')
        for path in results['to_delete']:
            print(f'    × {path}')
        return

    results = migration.run()

    print(f'\nMigration complete:')
    print(f'  Converted: {results["converted"]}')
    print(f'  Deleted:   {results["deleted"]} (had both files)')

    if results['errors']:
        print(f'  Errors:    {len(results["errors"])}')
        for error in results['errors']:
            print(f'    ! {error}')


if __name__ == '__main__':
    main()
