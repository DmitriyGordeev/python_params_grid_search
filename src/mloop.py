import numpy


class Mloop:
    def __init__(self, arrays, core_callback, write_config):
        self.arrays = arrays
        self.dim = len(arrays)
        self.iArr = numpy.zeros(self.dim)
        self.core_callback = core_callback
        self.write_config = write_config
        self.params_and_configs = []  # this is array of tuples: (params, config_path)

    def stop(self):
        for i, v in enumerate(self.iArr):
            if v != len(self.arrays[i]):
                return False
        return True

    def number_of_itr(self):
        n = 1
        for a in self.arrays:
            n = n * len(a)
        return n

    def reset_rec(self, target_idx):
        if target_idx > 0:
            if self.iArr[target_idx] == len(self.arrays[target_idx]):
                self.iArr[target_idx - 1] = self.iArr[target_idx - 1] + 1
                for i in range(target_idx, len(self.iArr)):
                    self.iArr[i] = 0
                self.reset_rec(target_idx - 1)

    def reset(self):
        self.reset_rec(len(self.iArr) - 1)

    def core(self, Itr):
        self.params_and_configs.append(self.core_callback(Itr, self.iArr, self.arrays, self.write_config))

    def loop(self):
        for globalI in range(0, self.number_of_itr()):
            self.core(globalI)
            if self.stop():
                break
            self.iArr[len(self.iArr) - 1] = self.iArr[len(self.iArr) - 1] + 1
            self.reset()
