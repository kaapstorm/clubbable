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
of Celery broker.

Mail is sent with Mailgun directly, so you will not need a Heroku add-on for
Mailgun.

Follow Heroku `instructions for deployment`_.

Heroku CLI commands to initialise the database and create a superuser are::

    $ heroku run -a <app> python src/clubbable/manage.py migrate
    $ heroku run -a <app> python src/clubbable/manage.py createsuperuser


.. _GNU Affero GPL: http://www.gnu.org/licenses/agpl-3.0.html
.. _fork the project on GitHub: https://github.com/kaapstorm/clubbable
.. _instructions for deployment: https://devcenter.heroku.com/articles/git
