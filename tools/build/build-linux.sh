#!/usr/bin/env bash
set -euxo pipefail

ROOT=$(realpath $(dirname "$0")/../..)
BUILDDIR="$ROOT"/build/linux
PARALLEL_JOBS=6

make_lfk() {
  # clone pylfk
  git clone https://github.com/waverian/evolution-benchmark.git

  # build lfk-benchmark.so
  (
    mkdir -p evolution-benchmark/
    cd evolution-benchmark/

    cmake -S . -B build_cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_CONSOLE_APP=OFF -DBUILD_SHARED_LIBS=OFF
    cmake --build build_cmake

    # build pylfk
    python3 -m pip install bindings/python/
  )
}

compile_atlas() {
  python "$ROOT/tools/museum/museum_data_to_json.py" tools/museum/museum_data
}

compile_app() {
  APPDIR=$PWD/myapp
  
  # prebuild
  
  python "$ROOT"/tools/build/prebuild.py --inline_kv $APPDIR
  python "$ROOT"/tools/build/prebuild.py --cythonize $APPDIR

  python -OO -m compileall -b $APPDIR

  find $APPDIR -name "__pycache__" -print0 | /usr/bin/xargs -0 -P $PARALLEL_JOBS /bin/rm -rf

  rm "$APPDIR/main.pyc"
  cp "$ROOT/benchmarkapp/main.py" "$APPDIR/main.py"
}

rm -rf "$BUILDDIR" \
  && mkdir -p "$BUILDDIR"

(
  cd "$BUILDDIR"
  export HOME="$PWD"

  python3 -m venv venv
  source venv/bin/activate

  # Setup requirements
  python -m pip install --upgrade -r "$ROOT"/tools/build/requirements.txt -r "$ROOT"/tools/build/requirements.linux.txt

  compile_atlas
  cp -a "$ROOT"/benchmarkapp myapp

  make_lfk
  compile_app

  # Build
  cp "$ROOT"/tools/build/benchmarkapp.linux.onefile.spec ./
  python -m PyInstaller --clean benchmarkapp.linux.onefile.spec

  # Rename executable
  mv dist/Evobench.run dist/evobench.run
)
