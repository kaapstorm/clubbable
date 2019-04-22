web: gunicorn --chdir src/clubbable clubbable.wsgi:application
worker: celery worker --workdir src/clubbable -A clubbable -l info
