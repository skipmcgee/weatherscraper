# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['weatherscraper.py'],
             pathex=['\\\\vmware-host\\Shared Folders\\Desktop\\weatherscraper-folder'],
             binaries=[],
             datas=[('README.md', '.'), ('LICENSE', '.'), ('day.png', '.'), ('img_notfound.jpeg', '.'), ('logo.png', '.'), ('night.png', '.')],
             hiddenimports=[],
             hookspath=['.'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=True)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='WeatherApp',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False , icon='logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='WeatherApp')
