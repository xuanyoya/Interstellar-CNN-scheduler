'''
Layer specification.
'''

class Layer(object):
    '''
    NN layer parameters.

    nifm: # ifmap channels.
    nofm: # ofmap channels.
    wifm: ifmap width.
    hifm: ifmap height.
    wofm: ofmap width.
    hofm: ofmap height.
    wfil: weight filter width.
    hfil: weight filter height.
    wstd: stride size in width dimension.
    hstd: stride size in height dimension.
    '''

    def __init__(self, nifm, nofm, wofm, hofm, wfil, hfil, wstd=1, hstd=1):
        self.nifm = nifm
        self.nofm = nofm
        self.wofm = wofm
        self.hofm = hofm
        self.wifm = wfil + (wofm - 1) * wstd
        self.hifm = hfil + (hofm - 1) * hstd
        self.wfil = wfil
        self.hfil = hfil
        self.wstd = wstd
        self.hstd = hstd
        assert self.wofm > 0
        assert self.hofm > 0

class FCLayer(Layer):
    '''
    NN fully-connected layer parameters.

    wifm/hifm = wfil/hfil, wstd/hstd = 1, wofm/hofm = 1
    '''

    def __init__(self, nifm, nofm, wfil, hfil):
        Layer.__init__(self, nifm, nofm, 1, 1, wfil, hfil)

