from quickcache.django_quickcache import get_django_quickcache

quickcache = get_django_quickcache(memoize_timeout=10, timeout=5 * 60)
