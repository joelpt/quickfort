import re

BUILD_TYPE_CFG = {

    'dig': {
        'init': None,
        'designate': 'moveto cmd ! setsize !'.split(),
        'samecmd': None,
        'diffcmd': ['cmd'],
        'submenukeys': '',
        'sizebounds': None,
        'custom': None,
        'setsize': 'setsize_standard'
     },

    'build': {
        'init': ['^'],
        'designate': 'exitmenu menu cmd moveto setsize ! % # %'.split(),
        'samecmd': ['cmd'],
        'diffcmd': ['cmd'],
        'submenukeys': ['i', 'w', 'e', 'C', 'T', 'M'],
        'sizebounds': (1, 1, 1, 1), # minwidth, maxwidth, minheight, maxheight
        'setsize': 'setsize_build',
        'custom': {

            # farm plot
            r'p':       { 'sizebounds': (1, 10, 1, 10),
                          'designate': 'exitmenu cmd moveto setsize !'.split() },

            # all constructions
            r'C.':      { 'sizebounds': (1, 10, 1, 10),
                          'designate': 'exitmenu menu cmd moveto setsize ! % setmats'.split(),
                          'setmats': 'setmats'
                        },

            # un/paved roads and bridges
            r'o|O|g':   { 'sizebounds': (1, 10, 1, 10) },

            # 5x5 siege workshop
            r'ws':      { 'sizebounds': (5, 5, 5, 5),
                          'setsize': 'setsize_fixed'
                        },

            # metalsmith forge, magma forge
            r'w[fv]':   { 'designate': 'exitmenu menu cmd moveto setsize ! % ! % # %'.split(),
                          'sizebounds': (3, 3, 3, 3),
                          'setsize': 'setsize_fixed'
                        },

            # 3x3 workshops other than those already accounted for
            r'w[^sfv]': { 'sizebounds': (3, 3, 3, 3),
                          'setsize': 'setsize_fixed'
                        },

            # trade depot
            r'D':       { 'designate': 'exitmenu cmd moveto setsize ! % ! % # %'.split(),
                          'sizebounds': (5, 5, 5, 5),
                          'setsize': 'setsize_fixed'
                        },

            # screw pump
            r'Ms':      { 'designate': 'exitmenu menu cmd moveto ! ! ! ! %'.split() },

            # horizontal and vertical axles
            r'Mh':      { 'sizebounds': (1, 10, 1, 1) },
            r'Mv':      { 'sizebounds': (1, 1, 1, 10) }

            }
    },

    'place': { # place stockpiles
        'init': None,
        'designate': 'moveto cmd ! setsize !'.split(),
        'samecmd': None,
        'diffcmd': ['cmd'],
        'submenukeys': '',
        'sizebounds': None,
        'custom': None,
        'setsize': 'setsize_standard'
    },

    'query': { # set building/task prefs
        'init': None,
        'designate': 'moveto cmd ! setsize !'.split(),
        'samecmd': None,
        'diffcmd': ['cmd'],
        'submenukeys': '',
        'sizebounds': None,
        'custom': None,
        'setsize': 'setsize_standard'
    }
}

class BuildConfig:

    def __init__(self, build_type, options):
        self.build_type = build_type
        # print build_type
        self.config = BUILD_TYPE_CFG[build_type]
        # print self.config

    def get(self, label, forkey=None):
        # return custom config value for matching key; if no match
        # for forkey is found the buildtype default will be used instead
        if forkey:
            custom = self.config.get('custom') or {}
            for k in custom:
                if re.match(k, forkey):
                    if label in custom[k]:
                        # print 'label %s forkey %s response %s' % (label, forkey, custom[k][label])
                        return custom[k][label]
        # return standard config value of this build type
        # print 'label %s forkey %s response %s' % (label, forkey, self.config.get(label))
        return self.config.get(label)

