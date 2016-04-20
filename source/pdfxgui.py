#!/usr/bin/env python3
import os
import sys
import os.path
from urllib.parse import urlparse
from random import randrange, choice
from time import sleep
from collections import namedtuple

# from PyQt5.QtWidgets import
from PyQt5.QtGui import QGuiApplication, QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView
from PyQt5.QtQml import QQmlApplicationEngine, QQmlEngine
from PyQt5.QtCore import QObject, QUrl, Qt, QVariant, pyqtSignal, QThread, QSortFilterProxyModel, QAbstractListModel, QAbstractTableModel, QModelIndex
from PyQt5.QtQml import QJSValue
from PyQt5 import QtCore, QtQuick

# Sentry raven client
from raven import Client as SentryClient

# PDFx
import pdfx
from pdfx.downloader import check_refs, download_refs

# Local modules
# from threadpool import ThreadPool
import settings

__version__ = "0.1.0"
__author__ = "Chris Hager"
__email__ = "chris@linuxuser.at"
__contact__ = "https://www.metachris.com"
__copyright__ = "Copyright 2015 Chris Hager"

IS_FROZEN = False
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        IS_FROZEN = True
        BUNDLE_DIR = sys._MEIPASS
else:
        # we are running in a normal Python environment
        BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))

SENTRY = SentryClient(settings.SENTRY_CLIENT_URI)

ERROR_FILE_NOT_FOUND = 1
ERROR_DOWNLOAD = 2
ERROR_PDF_INVALID = 4

REF_TEST = namedtuple('ref', ['ref', 'reftype'])
REFS_TEST = [
    REF_TEST("http://doc.qt.io/qt-5/qml-qtquick-controls-tableview.html", "url"),
    REF_TEST("https://docs.python.org/2/library/collections.html#collections.namedtuple", "url"),

    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/BROKENSefa12a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Cure10b.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Snyd07a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/MacI01b.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Neve14a_0.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Epst05a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Ruiz13a_kinematics_ribbon_fin.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Snyd12a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/MacI01a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Nels06a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/IRS13.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Mama16a_ACC2016_0.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/MacI11a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Neve13a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Cure10a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/MacI13a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/Shir09a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/MacI00a.pdf", "pdf"),
    REF_TEST("http://nxr.northwestern.edu/sites/default/files/publications/MacI01d.pdf", "pdf"),

    REF_TEST("mailto:a@b.com", "email"),
]

PDFX_INSTANCES = {}
MAINWINDOW_INSTANCE = None

# class MyTableModel(QAbstractListModel):
#     def __init__(self, datain, headerdata, parent=None, *args):
#         QAbstractListModel.__init__(self, parent, *args)
#         self.arraydata = datain * 2
#         self.headerdata = headerdata
#
#     def rowCount(self, parent=QModelIndex()):
#         print("rc", len(self.arraydata))
#         return len(self.arraydata)
#
#     def data(self, index, role=QtCore.Qt.DisplayRole):
#         print("data", index, role)
#         if not index.isValid():
#             return QVariant()
#         elif role != Qt.DisplayRole:
#             return QVariant()
#         return QVariant(self.arraydata[index.row()][index.column()])
#
#     def headerData(self, col, orientation, role):
#         print("headerdata")
#         if orientation == Qt.Horizontal and role == Qt.DisplayRole:
#             return QVariant(self.headerdata[col])
#         return QVariant()
#
#     def flags(self, index):
#         return QtCore.Qt.ItemIsEnabled


class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain * 2
        self.headerdata = headerdata

    def rowCount(self, parent=QModelIndex()):
        print("rc", len(self.arraydata))
        return len(self.arraydata)

    def columnCount(self, parent=QModelIndex()):
        print("cc")
        return len(self.arraydata[0])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        print("data", index, role)
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled


class SortFilterProxyModel(QSortFilterProxyModel):
    # https://wiki.python.org/moin/PyQt/Sorting%20numbers%20in%20columns
    def lessThan(self, left_index, right_index):
        left_var = left_index.data(Qt.EditRole)
        right_var = right_index.data(Qt.EditRole)

        try:
            return float(left_var) < float(right_var)
        except (ValueError, TypeError):
            pass
        return left_var < right_var


class DownloadQThread(QThread):
    download_item_started = pyqtSignal(object)
    download_item_finished = pyqtSignal(object, str)
    download_finished = pyqtSignal()

    def __init__(self, refs, target_folder):
        super(DownloadQThread, self).__init__()
        self.refs = refs
        self.target_folder = target_folder

    def run(self):
        print("\Downloading %s PDFs..." % len(self.refs))
        download_refs(self.refs, self.target_folder,
                      signal_item_started=self.download_item_started.emit,
                      signal_item_finished=self.download_item_finished.emit)
        self.download_finished.emit()


class CheckLinksQThread(QThread):
    checking_links_item_started = pyqtSignal(object)
    checking_links_item_finished = pyqtSignal(object, str)
    checking_links_finished = pyqtSignal()

    def __init__(self, refs):
        super(CheckLinksQThread, self).__init__()
        self.refs = refs

    def run(self):
        print("\nChecking %s URLs for broken links..." % len(self.refs))
        check_refs(self.refs,
                   signal_item_started=self.checking_links_item_started.emit,
                   signal_item_finished=self.checking_links_item_finished.emit)
        self.checking_links_finished.emit()


class OpenPdfQThread(QThread):
    signal_item_start = pyqtSignal(str)
    signal_item_extract_page = pyqtSignal(str, int)
    signal_item_error = pyqtSignal(str, int)
    signal_item_finished = pyqtSignal(str)
    signal_finished = pyqtSignal()

    def __init__(self, pdf_uris):
        super(OpenPdfQThread, self).__init__()
        self.pdf_uris = pdf_uris

    def run(self):
        global PDFX_INSTANCES
        for uri in self.pdf_uris:
            def signal_item_extract_page(curpage):
                self.signal_item_extract_page.emit(uri, curpage)

            print("Opening %s..." % uri)
            self.signal_item_start.emit(uri)

            try:
                PDFX_INSTANCES[uri] = pdfx.PDFx(uri, signal_item_extract_page)
            except pdfx.exceptions.FileNotFoundError as e:
                print("File not found")
                self.signal_item_error.emit(uri, ERROR_FILE_NOT_FOUND)
                continue
            except pdfx.exceptions.DownloadError as e:
                print("Download error")
                self.signal_item_error.emit(uri, ERROR_DOWNLOAD)
                continue
            except pdfx.exceptions.PDFInvalidError as e:
                print("PDF invalid error")
                self.signal_item_error.emit(uri, ERROR_PDF_INVALID)
                continue

            # sleep(3)
            self.signal_item_finished.emit(uri)
        self.signal_finished.emit()


class PdfDetailWindow:
    QML_FILE = "qml/PdfDetailsWindow.qml"
    window = None

    references = []
    num_references = 0

    check_links_thread = None
    dl_thread = None

    cur_download = 0
    num_downloads = 0

    def __init__(self, pdf_uri, fake=False):
        self.fake = fake

        # Create window
        self.engine = QQmlApplicationEngine()
        self.engine.load(self.QML_FILE)
        self.window = self.engine.rootObjects()[0]
        self.window.setTitle(os.path.basename(pdf_uri))

        self.window.download.connect(self.download)
        self.window.signalCheckLinks.connect(self.checkLinks)
        self.window.shutdown.connect(self.onClosing)
        self.window.signalOpenMainWindow.connect(self.openMainWindow)

        if self.fake:
            # self.references = REFS_TEST
            self.references = []
        else:
            # Sort references by type
            ref_set = PDFX_INSTANCES[pdf_uri].get_references()
            self.references = sorted(ref_set, key=lambda ref: ref.reftype)
        self.num_references = len(self.references)
        self.window.setStatusText("%s references" % self.num_references)

        for ref in self.references:
            self.window.addReference(ref.ref, ref.reftype)

        # This works somewhat. Simply binds the list to the listModel variable
        # but does not support layoutChanged, etc.
        # refs = [QVariant({"ref": ref.ref, "type": ref.reftype, "status": ""}) for ref in self.references]
        # self.engine.rootContext().setContextProperty('listModel', refs)

        # Now we try building a real model we can use with a SortFilterProxyModel
        # see https://wiki.python.org/moin/PyQt/Sorting%20numbers%20in%20columns

        # self.model = MyTableModel(refs*2, ["ref", "type", "status"])
        # self.window.setModel(self.model)
        #
        # self.model = QStandardItemModel()
        # for index, ref in enumerate(self.references):
        #     row = QStandardItem()
        #     row.setData(QVariant({
        #         "ref": ref.ref,
        #         "type": ref.reftype,
        #         "status": ""
        #     }))
        #     # row.setData(QVariant([ref.ref, ref.reftype, ""]))
        #     self.model.appendRow([row])
        # self.window.setModel(self.model)


        # self.model2 = SortFilterProxyModel()
        # self.model2.setSourceModel(self.model)
        # self.window.setModel(self.model2)

    def onClosing(self):
        print("XX Closing")
        # if self.check_links_thread:
        #     self.check_links_thread.quit()

    def openMainWindow(self):
        global MAINWINDOW_INSTANCE
        if not MAINWINDOW_INSTANCE:
            MAINWINDOW_INSTANCE = PDFxGui()
        MAINWINDOW_INSTANCE.window.show()
        MAINWINDOW_INSTANCE.window.raise_()
        MAINWINDOW_INSTANCE.window.requestActivate()

    def download(self, selected_item_indexes, target_folder_uri):
        """
        selected_item_indexes is a [QJSValue](http://doc.qt.io/qt-5/qjsvalue.html) Array
        """
        # Parse file:/// uri to local path
        parsed_path = urlparse(target_folder_uri)
        target_folder = os.path.abspath(parsed_path.path)
        print("targetfolder:", target_folder)

        # Get selected item indexes
        num_items_selected = selected_item_indexes.property("length").toInt()
        item_indexes = [selected_item_indexes.property(index).toInt() for index in range(num_items_selected)]

        # Extract only PDF references
        refs = []
        for item_index in item_indexes:
            if self.references[item_index].reftype in ["pdf"]:
                refs.append(self.references[item_index])

        if not refs:
            self.window.setStatusText("No pdf documents selected")
            self.window.downloadFinished()
            return

        # Filter out only "url" and "pdf" references
        self.num_downloads = len(refs)
        self.cur_downloaded = 0
        self.num_downloads_errors = 0

        def signal_download_item_finished(ref, status):
            index = self.references.index(ref)
            self.cur_downloaded += 1
            if status != "200":
                self.num_downloads_errors += 1
            print("done:", self.cur_downloaded, status)
            self.window.setStatusText("Downloaded %s of %s..." % (self.cur_downloaded, self.num_downloads))
            self.window.setStatusProgress(float(self.cur_downloaded) / float(self.num_downloads))
            self.window.checkLinksStatusCodeReceived(index, status)

        def signal_download_finished():
            self.window.setStatusText("Downloaded %s pdf documents (%s errors)" % (self.num_downloads, self.num_downloads_errors))
            self.window.downloadFinished()

        self.window.setStatusText("Downloading %s pdf documents..." % self.num_downloads)
        self.window.setStatusProgress(0)

        self.dl_thread = DownloadQThread(refs, target_folder)
        self.dl_thread.download_item_finished.connect(signal_download_item_finished)
        self.dl_thread.download_finished.connect(signal_download_finished)
        self.dl_thread.start()

    def checkLinks(self):
        print("start checking links...")

        # Filter out only "url" and "pdf" references
        refs = [ref for ref in self.references if ref.reftype in ["url", "pdf"]]
        self.num_checks_total = len(refs)
        self.num_checks_current = 0
        self.num_checks_errors = 0

        def signal_checking_links_item_finished(ref, status_code):
            self.num_checks_current += 1
            if status_code != "200":
                self.num_checks_errors += 1
            print("checked %s/%s. [%s] %s" % (self.num_checks_current, self.num_checks_total, status_code, ref))
            self.window.setStatusText("Checked link %s of %s..." % (self.num_checks_current, self.num_checks_total))
            self.window.setStatusProgress(float(self.num_checks_current) / float(self.num_checks_total))

            index = self.references.index(ref)
            self.window.checkLinksStatusCodeReceived(index, status_code)

        def signal_checking_links_finished():
            text = "Checked %s links (%s errors)" % (self.num_checks_total, self.num_checks_errors)
            self.window.setStatusText(text)
            self.window.checkLinksFinished()

        self.window.setStatusText("Checking links...")
        self.window.setStatusProgress(0)

        self.check_links_thread = CheckLinksQThread(refs)
        self.check_links_thread.checking_links_item_finished.connect(signal_checking_links_item_finished)
        self.check_links_thread.checking_links_finished.connect(signal_checking_links_finished)
        self.check_links_thread.start()


class PDFxGui:
    QML_FILE = "qml/MainWindow.qml"
    window = None
    threads = []
    pdf_windows = []

    def __init__(self):
        self.threads = []
        if not self.window:
            # Create and setup window
            self.engine = QQmlApplicationEngine()
            self.engine.load(self.QML_FILE)
            self.window = self.engine.rootObjects()[0]

            # Connect signals
            self.window.signalOpenPdfs.connect(self.open_pdf)

    def open_pdf(self, urls):
        num_pdfs = urls.property("length").toInt()
        pdf_urls = [urls.property(index).toString() for index in range(num_pdfs)]
        if len(pdf_urls) == 0:
            return

        def signal_item_start(uri):
            print("started:", uri)
            self.window.setStatusText("Opening %s..." % (os.path.basename(uri)))

        def signal_item_finished(uri):
            print("finished:", uri)
            win = PdfDetailWindow(uri)
            win.window.show()
            self.pdf_windows.append(win)

        def signal_item_error(uri, error):
            print("error:", uri, error)

        def signal_item_extract_page(uri, curpage):
            print("page:", curpage)
            self.window.setStatusText("Reading page %s of %s..." % (curpage, os.path.basename(uri)))

        def signal_finished():
            print("all finished")
            self.window.setState("")
            self.window.setStatusText("")

        self.window.setState("busy")
        open_thread = OpenPdfQThread(pdf_urls)
        open_thread.signal_item_start.connect(signal_item_start)
        open_thread.signal_item_extract_page.connect(signal_item_extract_page)
        open_thread.signal_item_finished.connect(signal_item_finished)
        open_thread.signal_item_error.connect(signal_item_error)
        open_thread.signal_finished.connect(signal_finished)
        open_thread.start()
        self.threads.append(open_thread)


if __name__ == "__main__":
    # SENTRY.captureMessage("ello")

    os.chdir(BUNDLE_DIR)
    print('frozen', IS_FROZEN)
    print('bundle dir is', BUNDLE_DIR)
    print('sys.argv[0] is', sys.argv[0])
    print('sys.executable is', sys.executable)
    print('os.getcwd is', os.getcwd())

    app = QGuiApplication(sys.argv)

    MAINWINDOW_INSTANCE = PDFxGui()
    MAINWINDOW_INSTANCE.window.show()

    # win1 = PdfDetailWindow("/tmp/some-test-funky.pdf", fake=True)
    # win1.window.show()

    try:
        status_code = app.exec_()
    except:
        # if this is packaged by PyInstaller, report crashes to sentry
        if IS_FROZEN:
            SENTRY.captureException()
        raise
    finally:
        sys.exit(status_code)

    # print(self.app)
    # print(dir(self.app))
    # self.app.setWindowIcon(QIcon("icon.ico"))
    # self.app.setWindowTitle("Foo")
    # self.app.setOrganizationName("Jeena")
    # self.app.setOrganizationDomain("jeena.net")
    # self.app.setApplicationName("FeedTheMonkey")
