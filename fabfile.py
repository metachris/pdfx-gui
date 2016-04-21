"""
You can see all commands with `$ fab -l`. Typical usages:
"""
import os
from fabric.api import local, run, env
from fabric.context_managers import prefix, shell_env
from fabric.operations import prompt
import source.settings

env.use_ssh_config = True

# Current app version
VERSION = source.settings.__version__   # eg. 1.1.0
VERSION_FN = VERSION.replace(".", "_")  # eq. 1_1_0

# Change to fabfile directory, to make relative paths work
DIR_SCRIPT = os.path.dirname(os.path.realpath(__file__))
os.chdir(DIR_SCRIPT)

DISTPATH = os.path.join(DIR_SCRIPT, "dist")
WORKPATH = os.path.join(DIR_SCRIPT, "build")


def _chdir(relpath="."):
    os.chdir(os.path.join(DIR_SCRIPT, relpath))


def version(semverVersion=None):
    """ Update __version__ strings """
    _chdir("source")
    if not semverVersion:
        semverVersion = prompt("Enter new semantic version:")
        if not semverVersion:
            print("Error: Need a valid version!")
            return

    # Update the __version__ strings now
    local("""grep "__version__ =" * -rl | xargs sed -i 's/__version__ =.*./__version__ = "%s"/g' """ % semverVersion)


def clean():
    """ Remove all cached and temporary files as well as the dist folder """
    _chdir()
    local("find ./ -name *.pyc -exec rm -f {} \;")
    local("rm -rf build dist __pycache__ source/__pycache__")


def buildAppOSX(file_spec="pdfxgui-onefile.spec"):
    """ Build PDFx.app """
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

    _chdir("dist")
    fn = "PDFx-%s.zip" % VERSION_FN 
    local("zip -r %s PDFx.app" % fn)

    print("-" * 20)
    print("Successfully build: dist/PDFx, dist/PDFx.app, dist/%s" % fn)


def uploadToS3(fn=None):
    if not fn:
        fn = "dist/PDFx-%s.zip" % VERSION_FN
    print("Uploading %s to S3..." % fn)
    if not os.path.isfile(fn):
        print("Error: file not found")
        exit(1)

    cmd = "aws s3 cp %s s3://pdfx/downloads/ --acl public-read" % fn
    local(cmd)

    url = "https://s3.amazonaws.com/pdfx/downloads/%s" % os.path.basename(fn)
    print("Upload successful. Link: %s" % url)

# def makeSpec():
#     _chdir("source")
#     cmd = """pyi-makespec \
#         --name pdfxgui \
#         --onefile \
#         --windowed \
#         --icon images/icon.icns \
#         --osx-bundle-identifier com.metachris.pdfx \
#         pdfxgui.py"""
#     local(cmd)
