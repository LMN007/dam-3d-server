
from flask import session, jsonify
from functools import wraps

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Auth:
    def __init__(self, *, not_login, disable_must_login=False):
        self.not_login = not_login
        self.disable_must_login = disable_must_login
    
    def log(self, *args, **kw):
        print(bcolors.OKBLUE, *args, bcolors.ENDC,  **kw)

    def verbose(self, *args, **kw):
        print(*args, **kw)

    def ok(self, *args, **kw):
        print(bcolors.OKGREEN, *args, bcolors.ENDC, **kw)

    def reject(self, reason):
        self.log('[Rejected: {}]'.format(reason), end='', flush=True)

    def grant(self):
        self.ok('[Granted]'.format(), end='', flush=True)

    def disabled(self):
        self.ok('[Disabled]'.format(), end='', flush=True)

    def must_login(self, *fail):
        def auth_wrapper_fn(func):
            @wraps(func)
            def auth_wrapper(*args, **kw):
                if self.disable_must_login:
                    the_res = func(*args, **kw) 
                    self.disabled()
                    return the_res
                if (not 'logged_in' in session) or not session['logged_in']:
                    self.reject('not logged in')
                    if len(fail):
                        return jsonify(fail[0])
                    else:
                        return jsonify(self.not_login)
                else:
                    the_res = func(*args, **kw) 
                    self.grant() # make sure user's output is logged before us
                    return the_res
            return auth_wrapper
        return auth_wrapper_fn
