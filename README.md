## PDFx GUI

A PyQt5/QML graphical user interface for [PDFx](https://github.com/metachris/pdfx)


## Getting started

    # Install Qt dependencies
    $ brew install pyqt5

    # Create and activate virtual environment for Python 3
    $ pyvenv venv
    $ . venv/bin/activate

    # Install PDFx (dev branch)
    $ pip install -e git+https://github.com/metachris/pdfx@dev#egg=pdfx

    # Finally enable the system packages, in order to import PyQt5
    $ vi venv/pyvenv.cfg  # set `include-system-site-packages = true`
