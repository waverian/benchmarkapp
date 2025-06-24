#!/usr/bin/env bash
set -euxo pipefail

MODE=${1:-debug}
ROOT=$(realpath $(dirname "$0")/../..)

compile_atlas() {
  python "$ROOT/tools/museum/museum_data_to_json.py" tools/museum/museum_data
}


[[ -d "$ROOT"/build/android ]] \
  || mkdir -p "$ROOT"/build/android

(
  cd "$ROOT"/build/android
  export HOME="$PWD"
  export GRADLE_USER_HOME="$PWD"/.gradle
  export ANDROID_USER_HOME="$PWD"/.android
  if [[ ! -d "$GRADLE_USER_HOME" ]]; then
    mkdir "$GRADLE_USER_HOME"
  fi
  echo "org.gradle.jvmargs=-Xmx4096m">> "$GRADLE_USER_HOME"/gradle.properties

  python3 -m venv venv
  source venv/bin/activate

  python3 -m pip install --upgrade pip
  python3 -m pip install -r "$ROOT"/tools/build/requirements.android.txt

  compile_atlas

  # Remove APK if exists
  rm -rf bin

  rm -rf "$ROOT/build/android/src"
  rm -rf "$ROOT/build/android/recipes"
  cp -a "$ROOT/benchmarkapp" "$ROOT/build/android/src"
  cp -a "$ROOT/tools/build/android/recipes" "$ROOT/build/android/"
  mv "$ROOT/build/android/src/app" "$ROOT/build/android/recipes/app/src"

  # Build
  (
    # prebuild
    python3 "$ROOT"/tools/build/prebuild.py --inline_kv "$ROOT/build/android/recipes/app/src"


    cd "$ROOT"/tools/build

    export BUILDOZER_BUILD_DIR="../../build/android/.buildozer"
    export BUILDOZER_BIN_DIR="../../build/android/bin"

    python3 -m buildozer --profile android android "$MODE"
  )

  if [[ "$MODE" == "release" ]]; then
    mv "$ROOT"/build/android/bin/evobench3-*.aab \
       "$ROOT"/build/android/bin/evobench.aab
  else
    mv "$ROOT"/build/android/bin/evobench3-*.apk \
       "$ROOT"/build/android/bin/evobench.apk
  fi
)

# sanity check
if [[ "$MODE" == "release" ]]; then
  PACKAGE="$ROOT"/build/android/bin/evobench.aab
else
  PACKAGE="$ROOT"/build/android/bin/evobench.apk
fi

[ -f "$PACKAGE" ] \
  || { echo Error: "$PACKAGE" doesn\'t exist >&2; exit 1; }

echo Successfully built "$PACKAGE"
