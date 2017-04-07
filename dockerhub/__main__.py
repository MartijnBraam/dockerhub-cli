from dockerhub import fetcher, builder


def parse_image_name(input):
    if ':' in input:
        image, tag = input.split(':')
    else:
        image = input
        tag = 'latest'
    return image, tag


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Docker hub image puller")
    parser.add_argument('image',
                        help='image in one of the following formats: image:tag repo/image:tag image repo/image')
    parser.add_argument('directory', help="Directory to unpack the image in")
    parser.add_argument('--tgz', help="Create a .tgz file instead of a unpacked directory", action="store_true")
    args = parser.parse_args()

    image, tag = parse_image_name(args.image)
    manifest = fetcher.pull_image(image, tag)

    if args.tgz:
        builder.build_tgz(manifest, args.directory)
    else:
        builder.build_rootfs(manifest, args.directory)
