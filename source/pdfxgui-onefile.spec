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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='pdfxgui',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='images/icon.icns')
app = BUNDLE(exe,
             name='pdfxgui.app',
             icon='images/icon.icns',
             bundle_identifier='com.metachris.pdfx')
