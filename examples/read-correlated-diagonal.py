from seismic_zfp.read import SzReader
from seismic_zfp.utils import get_correlated_diagonal_length
import segyio
import time
import os
import sys

from PIL import Image
import numpy as np
from matplotlib import cm

base_path = sys.argv[1]
LINE_NO = int(sys.argv[2])

CLIP = 0.2
SCALE = 1.0/(2.0*CLIP)

with SzReader(os.path.join(base_path, '0_2.sz')) as reader:
    t0 = time.time()
    for l in range(LINE_NO, LINE_NO+40):
        slice_sz = reader.read_correlated_diagonal(l)
    print("SzReader took", time.time() - t0)


im = Image.fromarray(np.uint8(cm.seismic((slice_sz.T.clip(-CLIP, CLIP) + CLIP) * SCALE)*255))
im.save(os.path.join(base_path, 'out_cd-sz.png'))


with segyio.open(os.path.join(base_path, '0.segy')) as segyfile:
    t0 = time.time()
    for l in range(LINE_NO, LINE_NO+40):
        diagonal_length = get_correlated_diagonal_length(l, len(segyfile.ilines), len(segyfile.xlines))
        slice_segy = np.zeros((diagonal_length, len(segyfile.samples)))
        if l >= 0:
            for d in range(diagonal_length):
                slice_segy[d, :] = segyfile.trace[(d+l)*len(segyfile.xlines) + d]
        else:
            for d in range(diagonal_length):
                slice_segy[d, :] = segyfile.trace[d*len(segyfile.xlines) + d - l]
    print("segyio took", time.time() - t0)

im = Image.fromarray(np.uint8(cm.seismic((slice_segy.T.clip(-CLIP, CLIP) + CLIP) * SCALE)*255))
im.save(os.path.join(base_path, 'out_cd-segy.png'))

im = Image.fromarray(np.uint8(cm.seismic(((slice_segy-slice_sz).T.clip(-CLIP, CLIP) + CLIP) * SCALE)*255))
im.save(os.path.join(base_path, 'out_cd-diff.png'))
