FROM python:3.6

# build target: "development" or "production"
ARG target

RUN apt-get update
# For importing Access database
RUN apt-get install -y mdbtools
# For Pillow
RUN apt-get install -y \
    python3-dev \
    libjpeg-dev \
    libpng-dev

# Prepare clubbable.tar.gz with:
# $ git archive --format=tar.gz --prefix=clubbable/ HEAD > clubbable.tar.gz
ADD clubbable.tar.gz /usr/src/
WORKDIR /usr/src/clubbable/src/clubbable/

COPY requirements/base.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY requirements/${target}.txt ./requirements_${target}.txt
RUN pip install --no-cache-dir -r requirements_${target}.txt
COPY requirements/import_legacy.txt ./requirements_legacy.txt
RUN pip install --no-cache-dir -r requirements_legacy.txt

COPY src/clubbable/clubbable/settings_${target}.py ./clubbable/settings.py
RUN python manage.py collectstatic --noinput
