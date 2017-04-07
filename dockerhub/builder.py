import os
import sys
import tarfile
import shutil
from xdg import XDG_CACHE_HOME


def get_cache(file):
    root = os.path.join(XDG_CACHE_HOME, 'dockerhub')
    return os.path.join(root, file)


def get_blobs(manifest):
    result = []
    for blob in manifest['fsLayers']:
        result.append(blob['blobSum'])
    return result


def build_tgz(manifest, target):
    blobs = get_blobs(manifest)
    if len(blobs) == 1:
        shutil.copy(get_cache('blobs/{}.tgz'.format(blobs[0])), '{}.tgz'.format(target))
    else:
        raise NotImplementedError("Multilayer extraction not implemented yet.")


def build_rootfs(manifest, target):
    if not os.path.isdir(target):
        os.makedirs(target)

    blobs = get_blobs(manifest)
    if len(blobs) != 1:
        raise NotImplementedError("Multilayer extraction not implemented yet.")

    layer = get_cache('blobs/{}.tgz'.format(blobs[0]))

    tar = tarfile.open(layer, 'r')
    for item in tar:
        tar.extract(item, target)
