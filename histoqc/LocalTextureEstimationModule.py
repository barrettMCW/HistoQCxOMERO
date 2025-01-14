import logging
import numpy as np
from skimage import  color
from distutils.util import strtobool
from skimage.feature import greycomatrix, greycoprops


#TODO tilewise?
def estimateGreyComatrixFeatures(s, params):
    prefix = params.get("prefix", None)
    prefix = prefix+"_" if prefix else ""

    logging.info(f"{s['filename']} - \tLocalTextureEstimationModule.estimateGreyComatrixFeatures:{prefix}")
    patch_size = int(params.get("patch_size", 32))
    npatches = int(params.get("npatches", 100))
    nlevels = int(params.get("nlevels", 8))
    feats = params.get("feats","contrast:dissimilarity:homogeneity:ASM:energy:correlation").split(':')
    invert = strtobool(params.get("invert", "False"))
    mask_name = params.get("mask_name","img_mask_use")


    img = s.getImgThumb(s["image_work_size"])[0]
    img = color.rgb2gray(img)

    mask = s[mask_name] if not invert else ~s[mask_name]
    maskidx = mask.nonzero()
    maskidx = np.asarray(maskidx).transpose()
    idx = np.random.choice(maskidx.shape[0], npatches)

    results = []

    for id in idx:
        r, c = maskidx[id, :]
        patch = img[r:r + patch_size, c:c + patch_size]
        glcm = greycomatrix(np.digitize(patch,np.linspace(0,1,num=nlevels),right=True), distances=[5],
                            angles=[0], levels=nlevels, symmetric=True, normed=True)

        results.append([greycoprops(glcm, prop=feat) for feat in feats])

    results = np.asarray(results).squeeze()

    for vals, feat in zip(results.transpose(), feats):
        s.addToPrintList(f"{prefix}{feat}", str(vals.mean()))
        s.addToPrintList(f"{prefix}{feat}_std", str(vals.std()))

    return
