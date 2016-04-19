"""
You can see all commands with `$ fab -l`. Typical usages:
"""
import os
from fabric.api import local, run, env
from fabric.context_managers import prefix, shell_env

# Change to fabfile directory, to make relative paths work
DIR_SCRIPT = os.path.dirname(os.path.realpath(__file__))
os.chdir(DIR_SCRIPT)

env.use_ssh_config = True

DISTPATH = os.path.join(DIR_SCRIPT, "dist")
WORKPATH = os.path.join(DIR_SCRIPT, "build")


def _chdir(relpath):
    os.chdir(os.path.join(DIR_SCRIPT, relpath))


def version():
    """ Update __version__ strings to the current Git version """
    raise Exception("Not yet implemented")


def clean():
    _chdir(".")
    local("find ./ -name *.pyc -exec rm -f {} \;")
    local("rm -rf build dist __pycache__ source/__pycache__")


def buildAppOSX(file_spec="pdfxgui-onefile.spec"):
    cmd = """pyinstaller \
        --log-level DEBUG \
        --distpath {distpath} \
        --workpath {workpath} \
        {specfile}""" \
        .format(
            distpath=DISTPATH,
            workpath=WORKPATH,
            specfile=file_spec
        )

    clean()
    _chdir("source")
    with shell_env(QT5DIR="/usr/local/Cellar/qt5/5.6.0"):
        local(cmd)


def makeSpec():
    _chdir("source")
    cmd = """pyi-makespec \
        --name pdfxgui \
        --onefile \
        --windowed \
        --icon images/icon.icns \
        --osx-bundle-identifier com.metachris.pdfx \
        pdfxgui.py"""
    local(cmd)
