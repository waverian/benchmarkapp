# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

data_files = [
    ( './yourapp/data', 'data' ),]

a = Analysis(['./yourapp/main.py'],
             pathex=['.'],
             binaries=[],
             datas=data_files,
             hiddenimports=['evolution_benchmark', 'plyer', 'plyer.platforms.macosx.filechooser', 'natsort', 'sh', 'sentry_sdk'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# exclude = ["pillow", "PIL"]
# a.binaries = [x for x in a.binaries if not x[0].startswith(tuple(exclude))]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='evobench',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          console=False,
          disable_windowed_traceback=False,
          target_arch='universal2',
          )

coll = COLLECT(exe,
               Tree('./yourapp'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='evobench')


app = BUNDLE(coll,
         name='evobench.app',
         console=False,
         icon='yourapp/data/icon.icns',
         bundle_identifier='com.waverian.evobench3',
         version=f'{os.environ["VERSION"]}',
         info_plist={
            'CFBundleIdentifier': 'com.waverian.evobench3',
            'CFBundleVersion': f'{os.environ["BUILD_NUMBER"]}',
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleShortVersionString': os.environ["BENCHMARKAPP_VERSION"],
            'LSMinimumSystemVersion': '10.9.0',
            'LSApplicationCategoryType': 'public.app-category.utilities',
            'LSRequiresIPhoneOS': 'NO',
            'ITSAppUsesNonExemptEncryption': 'NO',
            'ENABLE_USER_SCRIPT_SANDBOXING': 'NO'}
         )
