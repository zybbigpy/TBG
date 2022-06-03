import mtbmtbg.moire_tb as mtb
from mtbmtbg.config import DataType, ValleyType

import numpy as np


def _cal_flatband_var(emesh):
    n_band = emesh[0].shape[0]
    e1 = emesh[:, n_band//2]
    e2 = emesh[:, n_band//2-1]

    return np.var(np.append(e1, e2))


def cal_flatness(n_moire: int, n_g: int, datatype=DataType.CORRU):
    ret = mtb.tb_solver(n_moire, n_g, 10, disp=False, datatype=datatype, valley=ValleyType.VALLEY1)
    emesh = ret['emesh']
    v1_flatness = _cal_flatband_var(emesh)
    ret = mtb.tb_solver(n_moire, n_g, 10, disp=False, datatype=datatype, valley=ValleyType.VALLEY2)
    emesh = ret['emesh']
    v2_flatness = _cal_flatband_var(emesh)

    self.assertTrue(v1_flatness<2*1e-6)
    self.assertTrue(v2_flatness<2*1e-6)

    return (v1_flatness, v2_flatness)
