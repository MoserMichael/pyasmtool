#!/bin/bash

set -ex

# remove files not under git
#git clean -f -d

if [[ -d staging_dir ]]; then
    rm -rf staging_dir
fi
mkdir -p staging_dir/src/pyasmtools
mkdir -p staging_dir/tests

cp pyasmtools/*.py staging_dir/src/pyasmtools
cp requirements.txt staging_dir/
cp LICENSE.txt README.md staging_dir
cp pip-build/* staging_dir

if [[ -f build.zip ]]; then
    rm build.zip
fi

pushd staging_dir
python3 setup.py sdist bdist_wheel

python3 -m pip install --user --upgrade twine

# twine is put here right now, so add it to path.
export PATH=$HOME/Library/Python/3.9/bin:$PATH

twine check dist/*

cat <<EOF
*** upload ***
enter user: __token__
for password: <pypi api token>
EOF

python3 -m twine upload --verbose dist/*

popd


echo "*** build completed ***"

