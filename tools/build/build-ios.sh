#!/usr/bin/env bash
set -euxo pipefail
APPID=<REPLACE_WITH_YOUR_APPLE_ID(type number)>
APPNAME="evobench"
BUNDLEID="com.yourcompany.evobench3"

validate_n_upload() {
  echo "let's use productbuild for App Store Connect"

  xcrun altool --validate-app -f "$ROOT"/build/ios/bin/"$APPNAME".ipa --apple-id "$APPID"  --bundle-id "$BUNDLEID" --bundle-version "$BUILD_NUMBER"  --bundle-short-version-string "$BENCHMARKAPP_VERSION" -t ios -p @keychain:altoolp > "$APPNAME"_log.json
  #if validated then upload
  VALIDATE_WORKED=$(cat "$APPNAME"_log.json | tail -n 1)
  if [[ "$VALIDATE_WORKED" = "No errors validating archive at $APPNAME.ipa." ]]; then
    echo "Upload package to App Store Connect"
    xcrun altool --upload-package "$ROOT"/build/ios/bin/"$APPNAME".ipa --apple-id "$APPID" --bundle-id "$BUNDLEID" --bundle-version "$BUILD_NUMBER" --bundle-short-version-string "$BENCHMARKAPP_VERSION" -t ios -p @keychain:altoolp
  fi
}


ROOT=$(cd "$(dirname "$0")/../.."; pwd -P)

compile_atlas() {
  python "$ROOT/tools/museum/museum_data_to_json.py" tools/museum/museum_data
}

[[ -d "$ROOT"/build/ios ]] \
  || mkdir -p "$ROOT"/build/ios

(
  cd "$ROOT"/build/ios

  rm -rf Library; mkdir -p Library; ln -s "$HOME"/Library/Keychains Library/Keychains
  export HOME="$PWD"

  python3 -m venv venv
  source venv/bin/activate

  python -m pip install --upgrade pip
  python -m pip install -r "$ROOT"/tools/build/requirements.ios.txt

  compile_atlas

  # Remove bin
  rm -rf bin

  # Build
  (
    cd "$ROOT"/tools/build

    export BUILDOZER_BUILD_DIR="../../build/ios/.buildozer"
    export BUILDOZER_BIN_DIR="../../build/ios/bin"

    python3 -m buildozer --profile ${PROFILE:-ios} ios debug
  )

  mv "$ROOT"/build/ios/bin/evobench3-*.ipa/evobench3.ipa \
     "$ROOT"/build/ios/bin/"$APPNAME".ipa
  mv "$ROOT"/build/ios/bin/evobench3-*.ipa/manifest.plist \
     "$ROOT"/build/ios/bin/manifest.plist \
  || echo "manifest.plist doesn't exist"

  # enable the blow line to validate and upload the app to App Store Connect
  # validate_n_upload
)

# sanity check
PACKAGE="$ROOT"/build/ios/bin/"$APPNAME".ipa
[[ -f "$PACKAGE" ]] \
  || { echo Error: "$PACKAGE" doesn\'t exist >&2; exit 1; }

echo Successfully built "$PACKAGE"
