FROM python:3.6

RUN apt-get update
# For importing Access database
RUN apt-get install -y mdbtools
# For Pillow
RUN apt-get install -y \
    python3-dev \
    libjpeg-dev \
    libpng-dev

# build target: "development" or "production". Must have corresponding files
# requirements/${target}.txt and src/clubbable/clubbable/settings/${target}.py
ARG target=production

# Prepare clubbable.tar.gz with:
# $ git archive --format=tar.gz --prefix=clubbable/ HEAD > clubbable.tar.gz
ADD clubbable.tar.gz /usr/src/

WORKDIR /usr/src/clubbable/requirements/
RUN pip install --no-cache-dir -r base.txt
RUN pip install --no-cache-dir -r ${target}.txt
RUN pip install --no-cache-dir -r import_legacy.txt

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE clubbable.settings.${target}
EXPOSE 8000/tcp
WORKDIR /usr/src/clubbable/src/clubbable/
CMD ["/usr/local/bin/gunicorn", "--workers=2", "--bind=:8000", "clubbable.wsgi:application"]
