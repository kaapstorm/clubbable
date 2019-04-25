clubbable
=========

A web application for managing newsletters and image galleries for a club.


Deployment
----------

Heroku is the standard deployment environment, but you can find git branches
for building a Docker image, and for deploying to AWS Elastic Beanstalk in a
multi-container Docker environment.


Running locally
^^^^^^^^^^^^^^^

For Debian derivatives like Ubuntu, install system packages::

    $ sudo apt-get install python-dev libjpeg-dev libpng12-dev

Install Python requirements::

    $ sudo pip install -r requirements.txt

Create local configuration file::

    $ cp env/example env/local  # (where "local" is an arbitrary name)

Customise your configuration::

    $ $EDITOR env/local

Set environment variables::

    $ egrep -v '^#|^$' env/local | while read LINE ; do export $LINE ; done

Start the development web server::

    $ cd src/clubbable
    $ ./manage.py runserver


Documentation
-------------

Further documentation can be found in the "doc" directory.
