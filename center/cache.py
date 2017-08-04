from django.core.cache import cache


def cache_func(name, time=15):
    '''
    @cache_func('hello',15)
    def hello(a):
        return "hello%s"%a
    '''

    def _cache_func(func):
        def __cache_func(*args, **kwargs):
            data = cache.get(name)
            if not data:
                data = func(*args, **kwargs)
                cache.set(name, data, time)
            return data

        return __cache_func

    return _cache_func
