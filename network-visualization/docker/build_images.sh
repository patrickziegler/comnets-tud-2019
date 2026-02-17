#!/bin/bash
#>
#> Usage: build_images.sh
#>
#> Building docker images from all Dockerfiles found in the current
#> directory.
#>
#> The Dockerfiles should be named *.docker and their filenames will be
#> used as image names.
#>
#> Options:
#>    -h           show this help message and exit
#>
#> Examples:
#>
#>    ./build_images.sh
#>

SUFFIX=docker

while getopts "h" OPT; do
    case $OPT in
        h)
            cat `readlink -f "$0"` | awk '$0 ~ /^#>/ {print substr($0, 4, length($0)-1)}'
            exit;;
        \?)
            exit;;
    esac
done

shift $((OPTIND - 1))

flist=($(find *.${SUFFIX}))

for file in "${flist[@]}"; do
    echo "Building image from ${file}..."
    docker build -t "${file%.*}" -f "${file}" .
done
