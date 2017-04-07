import requests
import json
from tqdm import tqdm
from xdg import XDG_CACHE_HOME
import os

TOKEN = None


def get_cache():
    root = os.path.join(XDG_CACHE_HOME, 'dockerhub')
    if not os.path.isdir(os.path.join(root, 'blobs')):
        os.makedirs(os.path.join(root, 'blobs'))
    if not os.path.isdir(os.path.join(root, 'manifests')):
        os.makedirs(os.path.join(root, 'manifests'))
    return root


def pull_image(image_name, tag='latest'):
    image_name = parse_image_name(image_name)
    cache_manifest = os.path.join(get_cache(), 'manifests', '{}:{}.json'.format(image_name.replace('/', ':'), tag))
    if os.path.isfile(cache_manifest):
        print("Use image from cache")
        with open(cache_manifest) as handle:
            return json.loads(handle.read())
    else:
        manifest = get_image_info(image_name, tag)
        for layer in manifest['fsLayers']:
            pull_layer(image_name, layer['blobSum'])
        return manifest


def get_image_info(image_name, tag='latest'):
    global TOKEN
    image_name = parse_image_name(image_name)
    print("Loading manifest for docker image {}:{}".format(image_name, tag))
    url = 'https://index.docker.io/v2/{}/manifests/{}'.format(image_name, tag)
    response = requests.get(url, headers={"Accept": "application/json"})
    if response.status_code == 401:
        print("Getting authentication token for this image")
        authenticate = response.headers['www-authenticate']
        auth_type, fields = authenticate.split(' ', 1)
        fields = fields.split(",")
        auth_fields = {}
        for field in fields:
            key, value = field.split("=", 1)
            if value[0] == '"':
                value = value[1:-1]
            auth_fields[key] = value

        TOKEN = get_bearer_token(**auth_fields)
        response = requests.get(url, headers={"Accept": "application/json", "Authorization": "Bearer {}".format(TOKEN)})
    manifest = response.json()

    cache_file = os.path.join(get_cache(), 'manifests', '{}:{}.json'.format(image_name.replace('/', ':'), tag))
    with open(cache_file, 'w') as handle:
        handle.write(json.dumps(manifest))

    return manifest


def pull_layer(image_name, digest):
    image_name = parse_image_name(image_name)
    url = 'https://index.docker.io/v2/{}/blobs/{}'.format(image_name, digest)
    response = requests.get(url, headers={"Accept": "application/json", "Authorization": "Bearer {}".format(TOKEN)},
                            stream=True)

    chunk_size = 1024
    chunks = int(response.headers['Content-length']) / chunk_size
    filename = os.path.join(get_cache(), 'blobs', '{}.tgz'.format(digest))
    with open(filename, "wb") as handle:
        for chunk in tqdm(response.iter_content(chunk_size=chunk_size), desc="Pulling layer", unit='kB', total=chunks):
            if chunk:
                handle.write(chunk)


def parse_image_name(image_name):
    if '/' not in image_name:
        image_name = "library/{}".format(image_name)
    return image_name


def get_bearer_token(realm, scope, service):
    url = '{}?service={}&scope={}'.format(realm, service, scope)
    response = requests.get(url, headers={"Accept": "application/json"})
    data = response.json()
    return data['token']
