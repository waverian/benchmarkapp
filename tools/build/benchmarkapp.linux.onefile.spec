# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['myapp/main.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=['evolution_benchmark', 'sentry_sdk', 'distutils', 'plyer', 'plyer.platforms.macosx.filechooser', 'natsort', 'sh'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# Remove libstdc++, as it might not be compatible with the target system
a.binaries = [(name, path, type) for (name, path, type) in a.binaries
              if not name.startswith("libstdc++.so")]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          Tree('myapp/'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Evobench.run',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None, )
