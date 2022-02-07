import time


def maxtry(tryVal):
    def decorator(func):
        def wrapper(*args, **kw):
            i=0
            isexit=False
            while i<=tryVal and isexit==False:
                i+=1
                isexit=func(*args, **kw)
                if isexit==False:
                    time.sleep(5)
                else:
                    time.sleep(1)
            return isexit
        return wrapper
    return decorator
