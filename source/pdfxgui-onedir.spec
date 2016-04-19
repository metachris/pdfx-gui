# -*- mode: python -*-

block_cipher = None


datas = [
    ("qml/*.qml", "qml"),
    ("images/*.png", "images")
]

a = Analysis(['pdfxgui.py'],
             pathex=['/Users/chris/Projects/chris/pdf-link-extractor/pdfx-gui/source'],
             binaries=None,
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='pdfxgui',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='pdfxgui')
