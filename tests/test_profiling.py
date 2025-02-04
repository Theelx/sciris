'''
Test profiling functions.
'''

import sciris as sc
import numpy as np
import pytest


def test_loadbalancer():
    sc.heading('Testing loadbalancer')
    o = sc.objdict()

    # Test basic functions
    o.ncpus = sc.cpu_count()
    o.cpu = sc.cpuload()
    o.mem = sc.memload()

    # Test loadbalancer
    o.load = sc.loadbalancer(interval=0.1)
    return o


def test_memchecks():
    sc.heading('Testing memory checks')

    o = sc.objdict()

    print('\nTesting checkmem')
    o.mem = sc.checkmem(['small string', np.random.rand(243,589)], descend=True)

    print('\nTesting checkram')
    o.ram = sc.checkram()
    print(o.ram)

    return o


def test_profile():
    sc.heading('Test profiling functions')

    def slow_fn():
        n = 10000
        int_list = []
        int_dict = {}
        for i in range(n):
            int_list.append(i)
            int_dict[i] = i
        return

    def big_fn():
        n = 1000
        int_list = []
        int_dict = {}
        for i in range(n):
            int_list.append([i]*n)
            int_dict[i] = [i]*n
        return

    class Foo:
        def __init__(self):
            self.a = 0
            return

        def outer(self):
            for i in range(100):
                self.inner()
            return

        def inner(self):
            for i in range(1000):
                self.a += 1
            return

    foo = Foo()
    try:
        sc.mprofile(big_fn) # NB, cannot re-profile the same function at the same time
    except TypeError as E: # This happens when re-running this script
        print(f'Unable to re-profile memory function; this is usually not cause for concern ({E})')
    sc.profile(run=foo.outer, follow=[foo.outer, foo.inner])
    lp = sc.profile(slow_fn)

    return lp


def test_resourcemonitor():
    sc.heading('Testing resource monitor')

    o = sc.objdict()
    o.callback = []

    def callback(checkdata, checkstr):
        ''' Small function to test that callbacks work '''
        print('Callback works as intended')
        o.callback.append(checkdata)
        return

    with pytest.raises(sc.LimitExceeded):
        with sc.resourcemonitor(mem=0.001, interval=0.2, die=False) as resmon:
            print('Effectively zero memory limit')
            sc.timedsleep(0.5)
        raise resmon.exception
    o.resmon_died = resmon

    # As a standalone (don't forget to call stop!)
    resmon = sc.resourcemonitor(mem=0.95, cpu=0.99, time=0.2, interval=0.1, label='Load checker', die=False, callback=callback, verbose=True)
    sc.timedsleep(0.3)
    resmon.stop()
    print(resmon.to_df())

    o.resmon = resmon

    return o


#%% Run as a script
if __name__ == '__main__':
    sc.tic()

    lb = test_loadbalancer()
    mc = test_memchecks()
    lp = test_profile()
    rm = test_resourcemonitor()

    sc.toc()
    print('Done.')