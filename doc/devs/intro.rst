Documentation for Developers
============================

*clubbable* is an open source web application for managing newsletters and
image galleries for a club. It is licensed under the `GNU Affero GPL`_. You are
welcome to `fork the project on GitHub`_.


Hosting with Heroku
-------------------

**env/example** and **Procfile** will give you an idea of the resources you
will need. You will need a database and a Celery broker. The "Heroku Postgres"
and "Heroku Redis" add-ons would not be bad choices for these. *clubbable* uses
the Django ORM as a Celery result back-end, so RabbitMQ is also a good choice
of Celery broker. You may need to set the environment variable ``REDIS_URL``
to the Redis URL.

Mail is sent with Mailgun directly, so you will not need a Heroku add-on for
Mailgun.

Follow Heroku `instructions for deployment`_.

If you set the environment variable ``DEPLOY_ENV`` to "heroku", then
**settings.py** will use django_heroku to configure static files.

Heroku CLI commands to initialise the database and create a superuser are::

    $ heroku run -a <app> python src/clubbable/manage.py migrate
    $ heroku run -a <app> python src/clubbable/manage.py createsuperuser


Importing from a Microsoft Access database
------------------------------------------

*clubbable* is written for a club that uses a Microsoft Access database as a
primary data source. *clubbable* updates its own database by importing from the
Access database. It imports using a `microservice called dump_mdb`_ to dump
tables from an Access MDB file as CSV.

You can use *clubbable* without following this workflow. (In fact, I would
recommend avoiding it.)


.. _GNU Affero GPL: http://www.gnu.org/licenses/agpl-3.0.html
.. _fork the project on GitHub: https://github.com/kaapstorm/clubbable
.. _instructions for deployment: https://devcenter.heroku.com/articles/git
.. _microservice called dump_mdb: https://github.com/kaapstorm/dump_mdb
