#!/usr/bin/env bash
set -euxo pipefail
ROOT=$(realpath $(dirname "$0")/../..)
BUILDDIR="$ROOT"/build/windows
PARALLEL_JOBS=6

make_lfk() {
  # clone pylfk
  rm -rf evolution-benchmark
  git clone https://github.com/waverian/evolution-benchmark.git

  # Use x64 for pylfk
  (
    cd evolution-benchmark/

    cmake -S . -B build_cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DBUILD_CONSOLE_APP=OFF -G "Visual Studio 17 2022" -A x64 -T v141_xp
    cmake --build build_cmake --config Release

    mv bindings b
    mv b/python/ b/p

    # build pylfk
    python -m pip install -vvv b/p
  )

}

compile_app() {
  APPDIR=$PWD/myapp

  # prebuild
  python "$ROOT"/tools/build/prebuild.py --inline_kv $APPDIR
  VSPATH=$(/c/Program\ Files\ \(x86\)/Microsoft\ Visual\ Studio/Installer/vswhere.exe -products 'Microsoft.VisualStudio.Product.BuildTools' -latest -property installationPath)
  [[ ! -z "$VSPATH" ]] \
    || { echo Error: failed to identify build tools path >&2; exit 1; }

  # CMD with vcvars
  {
    echo call \"${VSPATH}\\VC\\Auxiliary\\Build\\vcvars64.bat\";
    echo python \"..\\..\\tools\\build\\prebuild.py\" --cythonize myapp;
    echo exit %ERRORLEVEL%;
  } | cmd.exe

  python -OO -m compileall -b $APPDIR

  # find $APPDIR -name "__pycache__" -print0 | xargs -0 -P $PARALLEL_JOBS rm -rf
  python -Bc "import pathlib; import shutil; [shutil.rmtree(p) for p in pathlib.Path('myapp').rglob('__pycache__')]"

  rm "$APPDIR/main.pyc"
  rm "$APPDIR/data/icon.ico"
  cp "$ROOT/benchmarkapp/main.py" "$APPDIR/main.py"
  cp "$ROOT/tools/build/windows/icon.ico" "$APPDIR/data/icon.ico"
}

compile_atlas() {
  python "$ROOT/tools/museum/museum_data_to_json.py" tools/museum/museum_data
}

pip list


[[ -d "$BUILDDIR" ]] \
  || mkdir -p "$BUILDDIR"

(
  cd "$BUILDDIR"
  export HOME="$PWD"

  python -m venv venv
  source venv/Scripts/activate

  pip list

  python -m pip install --upgrade pip
  python -m pip install -r "$ROOT"/tools/build/requirements.txt \
                        -r "$ROOT"/tools/build/requirements.windows.txt

  compile_atlas

  rm -rf myapp
  cp -a "$ROOT"/benchmarkapp myapp

  make_lfk
  compile_app

  # remove PyInstaller's dist directory if exists
  rm -rf dist

  cp "$ROOT"/tools/build/benchmarkapp.windows.spec ./
  python -m PyInstaller --clean benchmarkapp.windows.spec

  # Rename executable

  mv dist/"Evobench.exe" dist/evobench-windows-x64.exe
)

# sanity check
PACKAGE="$BUILDDIR"\\dist\\evobench-windows-x64.exe
[[ -f "$PACKAGE" ]] \
  || { echo Error: "$PACKAGE" doesn\'t exist >&2; exit 1; }

echo Successfully built "$PACKAGE"
