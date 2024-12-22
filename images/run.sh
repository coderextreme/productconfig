#!env bash
for i in `find ~/glTF-Sample-Models/2.0/ -name '*.gltf'`; do echo $i; npx x3d-image@latest -a -e -i $i -o `basename $i .gltf`.png; done

