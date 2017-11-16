# -*- coding: utf-8 -*-
'''
Simple functions related to changing behaviour if we're running on SPICE 
rather than a desktop.

The only thing to do at the moment is to change the matplotlib
plotting environment, so that it works with a headless machine.

This needs to be done BEFORE matplotlib has been loaded elsewhere!
From then on, you won't be able to plot to an x11 window,
but as you're running on SPICE that's ok...

Recommended usage:
import ukcp_common_analysis.spice_safe_plotting as ukcp_ssp ; ukcp_ssp.check()

~~~~~~~~~~~~~~~~~
NOTE:
There is an experimental matplotlib function that lets you do this
more flexibly, i.e. at any time:
https://matplotlib.org/api/pyplot_api.html?highlight=switch_backend#matplotlib.pyplot.switch_backend
e.g.
   plt.switch_backend("Agg")
This appears to work.

The current backend is obtained by saying:
   plt.get_backend()
# returns: u'TkAgg'

We may wish to use this in future,
but it's still sensible to check and set this once 
at the start of each program!
~~~~~~~~~~~~~~~~~

'''

def check(verbose=True):
    '''
    Check which machine we're on, 
    and make sure the backend is Agg if it's not a Desktop.
    '''
    import os
    machinename = os.uname()[1]
    if verbose: 
        print "Running on machine:", machinename

    if not (machinename.startswith('eld')): # or machinename.startswith('els')):
        # We're not running on a normal linux machine,
        # so we might be on SPICE
        # (SPICE machines are called things like "expspicesrv001")
        # or some other headless server.
        # We need to pre-load matplotlib and switch the plotting environment:
        import matplotlib
        matplotlib.use('Agg')
        # Could use plt.switch_backend("Agg")
        # but this is experimental...
        if verbose:
            import matplotlib.pyplot as plt
            print "Matplotlib plotting backend set to " + plt.get_backend()
    else:
        if verbose:
            import matplotlib.pyplot as plt
            print "Matplotlib plotting backend remains as " + plt.get_backend()
    return





if __name__=="__main__":
    print "==================================================================="
    print "You have tried to run   ukcp_standard_plots.spice_safe_plotting"
    print "from the command line.  This does nothing."
    print "Try importing the module and using it like this:"
    print "   import ukcp_standard_plots.spice_safe_plotting as ukcp_ssp ; ukcp_ssp.check()"
    print "====================================================================================="
#=========================================================================

