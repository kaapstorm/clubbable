from django.core.management import BaseCommand
from import_mdb.import_mdb import import_mdb


class Command(BaseCommand):
    help = 'Imports from a Microsoft Access database'

    def add_arguments(self, parser):
        parser.add_argument('filename', help='a Microsoft Access MDB file')

    def handle(self, *args, **options):
        import_mdb(options['filename'])
