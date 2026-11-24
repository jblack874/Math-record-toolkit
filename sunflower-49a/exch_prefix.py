import sys, io, contextlib, json, os
def load(exf='extras.json'):
    src = open('tilley_a.py').read().split('t0 = time.time()')[0]
    sys.argv = ['tilley_a.py', 'sunflower_check.py', '--extra-left', exf, '--extra-right', exf]
    g = {'__name__': 'tilley_prefix'}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, 'tilley_prefix', 'exec'), g)
    return g
