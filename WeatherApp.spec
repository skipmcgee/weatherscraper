# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['weatherscraper.py'],
             pathex=['\\\\vmware-host\\Shared Folders\\Desktop\\weatherscraper-1.0.3'],
             binaries=[],
             datas=[('day.png', '.'), ('img_notfound.jpeg', '.'), ('logo.png', '.'), ('night.png', '.')],
             hiddenimports=['tk', 'tkinter'],
             hookspath=['.'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='WeatherApp',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='logo.ico')
