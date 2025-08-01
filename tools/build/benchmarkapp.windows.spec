# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew

block_cipher = None

a = Analysis(['myapp\\main.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=['evolution_benchmark', 'sentry_sdk', 'cpufeature', 'plyer', 'plyer.platforms.macosx.filechooser', 'natsort', 'sh'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          Tree('myapp\\'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          [],
          name='Evobench',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          icon='myapp\\data\\icon.ico',
          console=False)
