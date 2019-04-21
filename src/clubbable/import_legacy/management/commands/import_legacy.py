from django.core.management import BaseCommand
from import_legacy.import_legacy import import_legacy


class Command(BaseCommand):
    help = 'Imports from a legacy database'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--incl-files', action='store_true',
                            help='Include documents and images')
        parser.add_argument('-p', '--path', help='Path to files')

    def handle(self, *args, **options):
        import_legacy(options['incl_files'], options['path'])
