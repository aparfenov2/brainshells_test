import sys, os, cv2, re, json
import numpy as np
from sklearn.decomposition import PCA


indir = 'out'
cnames = [os.path.splitext(fn)[0] for fn in os.listdir(indir)]
imgs = [cv2.imread(indir + '/' + fn) for fn in os.listdir(indir)]
# for fn in os.listdir(indir):
#     img = cv2.imread(indir + '/' + fn)
#     cname = os.path.splitext(fn)[0]

def image_colorfulness(image):
    (B, G, R) = cv2.split(image.astype("float"))
    rg = np.absolute(R - G)
    yb = np.absolute(0.5 * (R + G) - B)
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
    return stdRoot + (0.3 * meanRoot)

def image_colorfulness1(image):
    cx, cy = 36, 62
    return image[cy, cx, 2] != image[cy, cx, 1]

# for cn, img in zip(cnames, imgs):
#     print(cn, image_colorfulness(img))
# exit(0)
red = np.array([image_colorfulness1(img) for img in imgs], dtype=float)
# red = np.where(red > 50, 1.0, 0.0)
# print("red.shape", red.shape) # (52,)
# print(red)
# exit(0)

imgs = np.array(imgs, dtype=float)
# imgs = imgs[:,:,:,2]

# print(imgs.shape) # (52, 80, 55)
# exit(0)
# imgs /= 255
# Normalised [0,1]
minc = np.min(imgs, axis=(1,2)) # (52,3)
minc = minc[:,np.newaxis, np.newaxis] # (52,1,1)
ptp = np.ptp(imgs, axis=(1,2)) # (52, 3)
ptp = ptp[:,np.newaxis, np.newaxis] # (52,1,1)
imgs = (imgs - minc)/ptp # in range 0..1 for each channel, (52, 80, 57)

imgs = imgs.reshape(len(imgs),-1) # (52, 4400)
# imgs = np.hstack((imgs, red[:,np.newaxis])) # (52, 4401)
# print("imgs.shape", imgs.shape)
# exit(0)

img = imgs[10]
dist = np.linalg.norm(img-imgs, axis=1)
with np.printoptions(precision=3, suppress=True, threshold=sys.maxsize):
    print(dist)
exit(0)

pca = PCA(n_components=3)
reduced = pca.fit_transform(imgs) # (52, 3)
# print("reduced.shape", reduced.shape) # (52, 3)
# print(reduced)
# for cname, pc in zip(cnames, reduced):
#     print(cname, pc)
# with np.printoptions(precision=3, suppress=True, threshold=sys.maxsize):
#     print(pca.components_) # (3, 13680)
# print(base64.b64encode(pca.components_))
# print(pca.components_.tostring()) # (3, 13680)

print(pca.components_.shape) # (3, 4401)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

json_dump = json.dumps(pca.components_, cls=NumpyEncoder)
json_dump = json.dumps(json.loads(json_dump, parse_float=lambda x: round(float(x), 3)))
print(json_dump)

# print(pca.mean_.shape) # (13680,)
# print(np.min(pca.mean_), np.max(pca.mean_)) # (13680,)
# imgs = imgs - pca.mean_
# X_transformed = np.dot(imgs, pca.components_.T)

