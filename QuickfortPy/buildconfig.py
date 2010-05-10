import re

BUILD_TYPE_CFG = {

    'd': { # dig
        'init': [],
        'designate': 'moveto cmd ! setsize !'.split(),
        'samecmd': [],
        'diffcmd': ['cmd'],
        'allowlarge': [],
        'submenukeys': '',
        'sizebounds': (1, 1000, 1, 1000), # minwidth, maxwidth, minheight, maxheight
        'custom': {},
        'setsize': lambda keystroker, start, end: keystroker.setsize_standard(start, end)
     },

    'b': { # build
        'init': ['^'],
        'designate': 'exitmenu menu cmd moveto setsize ! % +! %'.split(),
        'samecmd': ['cmd'],
        'diffcmd': ['cmd'],
        'submenukeys': ['i', 'w', 'e', 'C', 'T', 'M'],
        'sizebounds': (1, 1, 1, 1), # minwidth, maxwidth, minheight, maxheight
        'setsize': lambda keystroker, start, end: keystroker.setsize_build(start, end),
        'custom': {

            # farm plot
            'p':        { 'sizebounds': (1, 10, 1, 10),
                          'designate': 'exitmenu cmd moveto setsize !'.split() },

            # all constructions, un/paved roads, and bridges
            #'C.|o|O|g': { 'sizebounds': (1, 10, 1, 10)#,
                          #'designate': 'exitmenu menu cmd moveto setsize ! % +! {Down} +! {Down} +! {Down} %'.split(),
            #            },
            # TODO try to get the multi-mats selection logic working like above 'designate'
            # probably it did not work because {Down} should be {NumpadAdd}

            # un/paved roads and bridges
            'o|O|g':     { 'sizebounds': (1, 10, 1, 10) },

            # 5x5 siege workshop
            'ws':       { 'sizebounds': (5, 5, 5, 5),
                          'setsize': lambda keystroker, start, end: keystroker.setsize_fixed(start, end)
                        },

            # metalsmith forge, magma forge
            'w[fv]':    { 'designate': 'exitmenu menu cmd moveto setsize ! % ! % +! %'.split(),
                          'sizebounds': (3, 3, 3, 3),
                          'setsize': lambda keystroker, start, end: keystroker.setsize_fixed(start, end)
                        },

            # trade depot
            'D':        { 'designate': 'exitmenu cmd moveto setsize ! % ! % +! %'.split(),
                          'sizebounds': (5, 5, 5, 5),
                          'setsize': lambda keystroker, start, end: keystroker.setsize_fixed(start, end)
                        },

            # screw pump
            'Ms':       { 'designate': 'exitmenu menu cmd moveto ! ! ! ! %'.split() },

            # horizontal and vertical axles
            'Mh':       { 'sizebounds': (1, 10, 1, 1) },
            'Mv':       { 'sizebounds': (1, 1, 1, 10) },

            # 3x3 workshops other than those already accounted for
            'w[^sfv]':  { 'sizebounds': (3, 3, 3, 3),
                          'setsize': lambda keystroker, start, end: keystroker.setsize_fixed(start, end)
                        }
            }
    },

    'p': { # place (stockpiles)
        'init': [],
        'designate': 'moveto cmd ! setsize !'.split(),
        'samecmd': [],
        'diffcmd': ['cmd'],
        'allowlarge': [],
        'submenukeys': '',
        'minsize': 0,
        'maxsize': 0,
        'custom': {},
        'setsize': lambda keystroker, start, end: keystroker.setsize_standard(start, end)
    },

    'q': { # query (set building/task prefs)
        'init': [],
        'designate': 'moveto cmd ! setsize !'.split(),
        'allowlarge': [],
        'submenukeys': '',
        'minsize': 0,
        'maxsize': 0,
        'custom': {},
        'setsize': lambda keystroker, start, end: keystroker.setsize_standard(start, end)
    }
}

class BuildConfig:

    def __init__(self, build_type, options):
        self.build_type = build_type
        self.config = BUILD_TYPE_CFG[build_type]

        # if build_type == 'b':
        #     if options.singleunitconstruction:
        #         self.config['maxsize'] = 1
        #         self.config['allowlarge'] = []

    def get(self, label, forkey=None):
        # return custom config value for matching key
        if forkey and 'custom' in self.config:
            custom = self.config['custom']
            for k in custom:
                if re.match(k, forkey):
                    if label in custom[k]:
                        return custom[k][label]
        # return standard config value of this build type
        return self.config[label]

