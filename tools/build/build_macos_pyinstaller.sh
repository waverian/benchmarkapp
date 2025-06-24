#!/usr/bin/env bash
set -euxo pipefail

ROOT=$(cd "$(dirname "$0")/../.."; pwd -P)
BUILDDIR="$ROOT"/build/macos
# CODESIGN_DEVELOPERID="Developer ID Application: <REPLACE, WITH , YOUR ID (ABCDEFGHIJ)>"
# CODESIGN_DISTRIBUTIONID="Apple Distribution: <REPLACE, WITH , YOUR ID (ABCDEFGHIJ)>"
# CODESIGN_INSTALLERID="3rd Party Mac Developer Installer: <REPLACE, WITH , YOUR ID (ABCDEFGHIJ)>"
PARALLEL_JOBS=6
# APPID=<YOUR_APPLE_ID(type number)>
BUNDLEID="com.yourcompany.evobench3"

setup_entitlements() {
  # Setup entitlement.plist for notorisation
  echo '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.application-identifier</key>
		<string>TQ8FYFHGMG.com.waverian.evobench3</string>		
		<key>keychain-access-groups</key>
		  <array>
		    <string>TQ8FYFHGMG.*</string>
		  </array>		
		<key>com.apple.developer.team-identifier</key>
		<string>TQ8FYFHGMG</string>
    <key>com.apple.security.app-sandbox</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.automation.apple-events</key>
    <true/>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
</dict>
</plist>' > entitlement.plist
}

#<key>com.apple.security.inherit</key>
#    <true/>
    

compile_evolution_benchmark() {
  # clone pylfk
  rm -rf evolution-benchmark
  git clone https://github.com/waverian/evolution-benchmark.git

  # build lfk-benchmark.dylib
  (
      cd evolution-benchmark/

      cmake -S . -B build_cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_BUILD_TYPE=Release -DBUILD_CONSOLE_APP=OFF -DBUILD_SHARED_LIBS=OFF -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64"
      cmake --build build_cmake

      # build pylfk
      python -m pip install bindings/python/ 
  )
}

compile_app() {
  APPDIR=$PWD/myapp
  python3 -m venv compile_env
  source compile_env/bin/activate
  
  pip install -r "$ROOT/tools/build/requirements.macos.txt"
  
  # prebuild
  python "$ROOT"/tools/build/prebuild.py --inline_kv $APPDIR

  find -E $APPDIR -name "__pycache__" -print0 | /usr/bin/xargs -0 -P $PARALLEL_JOBS /bin/rm -rf

  python "$ROOT"/tools/build/prebuild.py --cythonize $APPDIR

  python -OO -m compileall -b $APPDIR

  find -E $APPDIR -regex "(.*)\\.py" -print0 | /usr/bin/xargs -0 -P $PARALLEL_JOBS /bin/rm
  find -E $APPDIR -name "__pycache__" -print0 | /usr/bin/xargs -0 -P $PARALLEL_JOBS /bin/rm -rf

  deactivate
  rm -rf compile_env
  rm "$APPDIR/main.pyc"
  cp "$ROOT/benchmarkapp/main.py" "$APPDIR/main.py"
}

fix_icons() {
  # fix icns
  # Define the source image and the destination directory
  SOURCE_IMAGE="yourapp/data/icon.png"
  DEST_DIR="yourapp/data/icon.iconset"
  mkdir $DEST_DIR

  # Define the sizes for the icons
  SIZES=(512 256 128 32 16)

  # Loop through each size and create the corresponding image
  for SIZE in "${SIZES[@]}"; do
      sips -z $SIZE $SIZE $SOURCE_IMAGE --out "$DEST_DIR/icon_${SIZE}x${SIZE}.png"
      sips -z $((SIZE * 2)) $((SIZE * 2)) $SOURCE_IMAGE --out "$DEST_DIR/icon_${SIZE}x${SIZE}@2x.png"
  done

  iconutil --convert icns yourapp/data/icon.iconset
  rm -rf yourapp/data/icon.iconset
  ls yourapp/data/
}

cosign() {
  CODESIGNID=$1
  find -E dist/Evobench.app -regex "(.*)\\.so" -print0 | /usr/bin/xargs -0 -P 6 codesign -s "$CODESIGNID" --force --all-architectures --timestamp --options=runtime
  # We might get a huge speeup by removing the following 1 line
  # is the following even needed anymore? We already do the deep signing manually above.
  codesign -s "$CODESIGNID" --force --all-architectures --timestamp --options=runtime --deep dist/Evobench.app
  codesign -s "$CODESIGNID" --force --all-architectures --timestamp --options=runtime --entitlements entitlement.plist dist/Evobench.app
}

notarize_n_staple() {

  cp "$ROOT/tools/build/evobench3_macos_developerid_distribution.provisionprofile" dist/Evobench.app/Contents/embedded.provisionprofile
  cosign "$CODESIGN_DEVELOPERID"
  
  pushd dist
  # Verify our codesigning
  codesign --verify --strict --deep --verbose=4 ./Evobench.app

  
  # create zip
  ditto -c -k --keepParent ./Evobench.app ./Evobench.zip

  # Notarize the DMG and capture the request UUID
  xcrun notarytool submit Evobench.zip --keychain-profile "notarytool-password" --wait 2>&1 | tee Evobenchapp_log.json
  
  # Extract the Request UUID from the output
  REQUEST_UUID=$(cat Evobenchapp_log.json|grep id: |awk '{print $2}'| head -1)
  NOTORY_ACCEPTED=$(cat Evobenchapp_log.json | grep status| tail -n 1| awk '{print $2}')

  # Fetch and display the notarization log
  xcrun notarytool log "$REQUEST_UUID" --keychain-profile "notarytool-password" Evobenchapp_log.json
  # cat Evobenchapp_log.json
  echo "Details in Evobenchapp_log.json"
  echo Evobenchapp_log.json
  if [ $NOTORY_ACCEPTED = "Accepted" ]; then
    # staple ticket
    STAPLE_WORKED=$(xcrun stapler staple ./Evobench.app | tail -n 1)
    if [[ "$STAPLE_WORKED" = "The staple and validate action worked!" ]]; then
      echo "Staple worked"
      build_dmg
    fi
  fi
  popd
}

build_dmg() {
  # create dmg
  hdiutil create -volname "Evobench" -srcfolder ./Evobench.app -ov -format UDZO -imagekey zlib-level=9 -size 180M ./Evobench.dmg
}

validate_package() {
  cp "$ROOT/tools/build/evobench_macos_app_store_may_09.provisionprofile" "dist/Evobench.app/Contents/embedded.provisionprofile"
  cosign "$CODESIGN_DISTRIBUTIONID"
  
  pushd dist
  # Verify our codesigning
  codesign --verify --strict --deep --verbose=4 ./Evobench.app
  
  echo "let's use productbuild for App Store Connect"
  productbuild --sign "$CODESIGN_INSTALLERID" --component ./Evobench.app /Applications ./Evobench.pkg
  
  xcrun altool --validate-app -f ./Evobench.pkg --apple-id "$APPID"  --bundle-id "$BUNDLEID" --bundle-version "$BUILD_NUMBER"  --bundle-short-version-string "$BENCHMARKAPP_VERSION" -t macos -p @keychain:altoolp > evobench_log.json
  #if validated then upload
  #let's upload to testflight
  VALIDATE_WORKED=$(cat evobench_log.json| tail -n 1)
  if [[ "$VALIDATE_WORKED" = "No errors validating archive at 'Evobench.pkg'." ]]; then
    echo "Paclage ready to upload package to App Store Connect.  Can be uploaded post build."
    xcrun altool --upload-package ./Evobench.pkg --apple-id "$APPID" --bundle-id "$BUNDLEID" --bundle-version "$BUILD_NUMBER" --bundle-short-version-string "$BENCHMARKAPP_VERSION" -t macos -p @keychain:altoolp
  fi
}

move_app() {
  # move app
  rm -rf yourapp
  mv $APPDIR ./yourapp
  cp "$ROOT/tools/build/benchmarkapp.mac.spec" "./"
}

setup_pyobjus(){
  git clone https://kivy/kivy/pyobjus
  python -m pip install ./pyobjus
  rm -rf pyobjus
}


setup_env() {
  rm -rf ./venv
  python3 -m venv ./venv
  source venv/bin/activate

  pip install --upgrade pip
  python -m pip install pyinstaller
  python -m pip install -r "$ROOT"/tools/build/requirements.txt

  compile_evolution_benchmark

  python -m pip install -r "$ROOT"/tools/build/requirements.macos.txt
  compile_atlas
  setup_pyobjus
  echo Y | python -m pip uninstall pillow
  deactivate
}

clean_app() {
  cd $ROOT
  # make sure app is clean
  cd $BUILDDIR

  rm -rf Library; mkdir -p Library; ln -s "$HOME"/Library/Keychains Library/Keychains
  export HOME="$PWD"
}

build_app(){
  rm -rf dist

  source venv/bin/activate
  pyinstaller benchmarkapp.mac.spec
}

compile_atlas() {
  python "$ROOT/tools/museum/museum_data_to_json.py" tools/museum/museum_data
}

[[ -d $BUILDDIR ]] \
  || mkdir -p $BUILDDIR

(
  clean_app 
  setup_env
  
  find -E "$ROOT/benchmarkapp" -regex "(.*)\\.DS_Store" -print0 | /usr/bin/xargs -0 -P 6 /bin/rm
  rm -rf ./myapp
  
  cp -a "$ROOT"/benchmarkapp/ ./myapp

  APPDIR=$PWD/myapp
  compile_app
  setup_entitlements
  move_app
  fix_icons
  build_app

  # Enable the following line to notarize and staple the app
  # Make sure to replace the CODESIGN_DEVELOPERID and other ID with your own

  # notarize_n_staple
  # validate_package
)

# sanity check
PACKAGE="$ROOT"/build/macos/dist/Evobench.dmg
[[ -f "$PACKAGE" ]] \
  || { echo Error: "$PACKAGE" doesn\'t exist >&2; exit 1; }

echo Successfully built "$PACKAGE"
