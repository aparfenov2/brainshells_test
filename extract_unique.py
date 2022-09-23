import os, cv2, re
import numpy as np

indir = 'imgs_marked'
outdir = 'out'
os.makedirs(outdir, exist_ok=True)

for fn in os.listdir(indir):
    img = cv2.imread(indir + '/' + fn)
    bn = os.path.splitext(fn)[0]
    cnames = re.findall(r'(?:\d+|[AJKQ])[csdh]', bn)
    x1,y1 = 147, 590
    y2 = 670
    xstep = 71.66
    xwidth = 55
    crops = [img[y1:y2, int(xa):int(xb)] for xa, xb in zip(
        np.arange(x1, x1 + 4*xstep, xstep),
        np.arange(x1 + xwidth, x1 + xwidth + 4*xstep, xstep)
        )]
    for cn, crop in zip(cnames, crops):
        fout = f"{outdir}/{cn}.png"
        if os.path.exists(fout):
            print('-', end='', flush=True)
            continue
        print('+', end='', flush=True)
        cv2.imwrite(fout, crop)
