import copy
import re

#        layers = Transformer(layers, options.transform).transform()
class Transformer:

    def __init__(self, layers, transform_str):
        self.layers = layers
        self.transforms = self.parse_transform_str(transform_str)

        # put zup/zdown transforms at the end so we do x/y transforms first
        self.transforms.sort(cmp=lambda x, y: compare_transforms(x, y))

    def transform(self):
        print self.transforms
        for t in self.transforms:
            count, cmd = t
            if cmd == 'd':
                addlayers = copy.deepcopy(self.layers)
                for i in xrange(1, count):
                    self.layers.extend(copy.deepcopy(addlayers))
        return self.layers

    @staticmethod
    def parse_transform_str(transform_str):
        transforms = transform_str.split(';')
        readies = []
        for t in transforms:
            m = re.match(r'(\d+)?\s*(\w+)', t)
            (count, cmd) = m.group(1, 2)
            count = int(count) if count else 1
            readies.append((count, cmd))
        return readies


def compare_transforms(t, u):
    tz = t[1][0] in ('u', 'd')
    uz = u[1][0] in ('u', 'd')

    if tz and uz:
        return 0
    if tz:
        return 1
    if uz:
        return -1
    return 0
