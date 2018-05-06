import pickle as cPickle
import numpy as np
import glob


class InputData(object):

    def __init__(self, directory, batch_size=128, wildcard=None):
        self._directory = directory
        self._batch_size = batch_size
        self._wildcard = wildcard
        self._subset_file_names = self._fetch_pkl_filename()
        self._X = None
        self._label = None
        self._rand_idx = None
        self._is_load = False
        self._within_subset_cursor = 0
        self._subset_counter = 0
        self.epoch = 0

    def _fetch_pkl_filename(self):
        if self._wildcard is None:
            return glob.glob(self._directory + '*.pkl')
        else:
            return glob.glob(self._wildcard)

    def load(self, subset_counter=0):
        print(self._subset_file_names)

        print('From data_io.input.load: loading from file', self._subset_file_names[subset_counter])
        self._X, self._label = cPickle.load(open(self._subset_file_names[subset_counter], 'rb'))
        self._X = np.asarray(self._X)
        self._label = np.asarray(self._label)
        self._rand_idx = np.arange(self._X.shape[0])
        np.random.shuffle(self._rand_idx)
        self._is_load = True

    def next_batch(self):
        if not self._is_load or self._within_subset_cursor >= len(self._rand_idx):
            if self._subset_counter == 0:
                self.epoch += 1
            try:
                self.load(self._subset_counter)
            except (IOError, KeyError) as e:
                if self._subset_counter < len(self._subset_file_names) - 1:
                    self._subset_counter += 1
                else:
                    self._subset_counter = 0
                print('IOError or KeyError')
                return [], []

            self._within_subset_cursor = 0
            if self._subset_counter < len(self._subset_file_names) - 1:
                self._subset_counter += 1
            else:
                self._subset_counter = 0

        idx = self._rand_idx[self._within_subset_cursor: self._within_subset_cursor + self._batch_size]
        self._within_subset_cursor += self._batch_size
        X_batch = self._X[idx]
        y_batch = self._label[idx]

        return X_batch, y_batch




