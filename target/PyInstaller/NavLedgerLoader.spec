# -*- mode: python -*-

block_cipher = None


a = Analysis(['/Users/alex/nav-ledger-loader/src/main/python/main.py'],
             pathex=['/Users/alex/nav-ledger-loader/target/PyInstaller'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['/Users/alex/nav-ledger-loader/ledger/lib/python3.7/site-packages/fbs/freeze/hooks'],
             runtime_hooks=['/Users/alex/nav-ledger-loader/target/PyInstaller/fbs_pyinstaller_hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='NavLedgerLoader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False , icon='/Users/alex/nav-ledger-loader/target/Icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='NavLedgerLoader')
app = BUNDLE(coll,
             name='NavLedgerLoader.app',
             icon='/Users/alex/nav-ledger-loader/target/Icon.icns',
             bundle_identifier=None)
