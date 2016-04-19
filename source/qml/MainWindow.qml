import QtQuick 2.6
import QtQuick.Layouts 1.2
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.2
import QtQuick.Controls 1.2
import QtQuick.Controls.Styles 1.4

ApplicationWindow {
    id: window
    visible: true
    width: 400
    minimumWidth: 300
    // maximumWidth: 300
    height: 260
    minimumHeight: 200
    // maximumHeight: 200

    title: "PDFx"

    signal signalOpenPdfs(var uris)

    function setState(state) {
        windowStateGroup.state = state
    }

    function setStatusText(statusText) {
        statusLabel.text = statusText
    }

    function setStatusProgress(value) {
        statusProgressBar.value = value
    }

    function openPdfs(urls) {
        var pdfs = []
        var endsWithPDF = /pdf$/;
        urls.forEach(function(url) {
            if (endsWithPDF.test(url.toLowerCase())) {
                // console.log("is pdf:", url)
                pdfs.push(url)
            }
        });

        if (pdfs.length === 0) {
            console.log("No PDFs!")
            return false
        }

        window.signalOpenPdfs(pdfs)
        return true
    }

    StateGroup {
        id: windowStateGroup
        states: [
            State {
                PropertyChanges { target: busyIndicator; visible: false }
            },
            State {
                name: "busy"
                PropertyChanges { target: busyIndicator; visible: true }
            }
        ]
    }

    menuBar: MenuBar {
        Menu {
            title: "File"
            MenuItem {
                text: "Open..."
                shortcut: StandardKey.Open
                onTriggered: {
                    fileDialog.open()
                }
            }
            MenuItem {
                text: "about.*"
            }
            MenuItem {
                text: "preferences"
            }
            // Menu {
            //     title: "Open Recent"
            //
            //     MenuItem {
            //         text: "Nothing here"
            //     }
            // }
        }
    }

    Action {
        id: aboutAction
        text: "About"
        onTriggered: aboutDialog.open()
    }

    statusBar: StatusBar {
        RowLayout {
            anchors.fill: parent
            Label {
                id: statusLabel
                Layout.fillWidth: true
                Layout.minimumWidth: 150
                Layout.preferredWidth: 300
                Layout.maximumWidth: 300

                text: "Read Only"
            }

            ProgressBar {
                id: statusProgressBar
                Layout.fillWidth: true
                Layout.minimumWidth: 150
                Layout.preferredWidth: 300
                //Layout.maximumWidth: 300
                visible: false
            }
        }
    }

    Image {
        id: dropImage
        property real defaultOpacity: 0.3
        opacity: defaultOpacity

        source: "../images/drop-here.png"
        fillMode: Image.PreserveAspectFit
        anchors.fill: parent
        anchors.bottomMargin: 50
    }

    BusyIndicator {
        id: busyIndicator
        anchors.centerIn: parent
        visible: false
    }

    Button {
        anchors.top: dropImage.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width - 100
        anchors.topMargin: 10

        text : "Click to select PDF file"
        onClicked: {
            fileDialog.open()
            //
            // if (windowStateGroup.state === "busy")
            //     windowStateGroup.state = ""
            // else
            //     windowStateGroup.state = "busy"

        }
    }

    DropArea {
        id: dropArea
        anchors.fill: parent

        states: [
            // Default State
            State {
                PropertyChanges { target: dropImage; opacity: dropImage.defaultOpacity }
            },

            // State when item is being dragged
            State {
                when: dropArea.containsDrag
                PropertyChanges { target: dropImage; opacity: 1.0 }
            }
        ]

        onDropped: {
            var hasPdfs = openPdfs(drop.urls)
            drop.accepted = hasPdfs
        }
    }

    FileDialog {
        id: fileDialog
        title: "Please choose a PDF document"
        folder: shortcuts.home
        selectMultiple: true
        nameFilters: [ "PDF document (*.pdf)", "All files (*)" ]
        onAccepted: {
            openPdfs(fileDialog.fileUrls)
            fileDialog.folder = fileDialog.fileUrls[0]
        }
    }
}
