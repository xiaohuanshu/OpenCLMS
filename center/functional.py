from functools import wraps


def classmethod_cache(func):
    @wraps(func)
    def returned_wrapper(self):
        funcname = func.__name__
        if hasattr(self, '%s_cacle' % funcname):
            return getattr(self, '%s_cacle' % funcname)
        else:
            data = func(self)
            setattr(self, '%s_cacle' % funcname, data)
            return data

    return returned_wrapper
