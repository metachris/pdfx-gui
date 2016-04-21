import QtQuick 2.6
import QtQuick.Layouts 1.2
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.2
import QtQuick.Controls 1.2
import QtQuick.Controls.Styles 1.4

import "shared.js" as SharedScripts

ApplicationWindow {
    id: window
    visible: true

    signal download(var uris, string target_folder)
    signal signalCheckLinks()
    signal signalOpenPdfs(var uris)
    signal signalOpenMainWindow()
    signal signalShowAboutWindow()
    signal shutdown()

    onClosing: {
        console.log("BYE")
        shutdown()
    }

    function addReference(uri, type) {
        sourceModel.append({
            ref: uri,
            type: type,
            status: ""
        })
    }

    function setModel(model) {
        tableView.model = model
        // tableView.model.layoutChanged()
        console.log(model)
        console.log(model.rowCount())
        // console.log(model.data(0))
        // console.log(model.takeItem(0, 0))
    }

    function setStatusText(statusText) {
        statusLabel.text = statusText
    }

    function setStatusProgress(value) {
        statusProgressBar.value = value
    }

    function startDownload(targetFolder) {
        var items = []
        tableView.selection.forEach(function(rowIndex) { items.push(rowIndex) })
        windowStateGroup.state = "busy"
        statusColumn.visible = true
        download(items, targetFolder)
    }

    function downloadFinished() {
        // revert to default state
        windowStateGroup.state = ""
    }

    function checkLinks() {
        windowStateGroup.state = "busy"
        statusColumn.visible = true
        signalCheckLinks()
    }

    function checkLinksFinished() {
        windowStateGroup.state = ""
    }

    function checkLinksStatusCodeReceived(rowIndex, statusCode) {
        var color = statusCode === "200" ? "green" : "red"
        tableView.rowColors[rowIndex] = color
        tableView.model.get(rowIndex).status = statusCode.toString()
        tableView.model.layoutChanged()
    }

    StateGroup {
        id: windowStateGroup
        states: [
            State {
                PropertyChanges { target: statusProgressBar; visible: false }
                PropertyChanges { target: btnDownload; enabled: true }
                PropertyChanges { target: btnCheckLinks; enabled: true }
            },
            State {
                name: "busy"
                PropertyChanges { target: statusProgressBar; visible: true }
                PropertyChanges { target: btnDownload; enabled: false }
                PropertyChanges { target: btnCheckLinks; enabled: false }
            }
        ]
    }

    menuBar: MenuBar {
        Menu {
            title: "File"
            MenuItem {
                text: "New Window"
                shortcut: StandardKey.New
                onTriggered: {
                    console.log("pdfwindow new")
                    signalOpenMainWindow()
                }
            }
            MenuItem {
                text: "Close Window"
                shortcut: StandardKey.Close
                onTriggered: {
                    window.close()
                }
            }
            // MenuItem {
            //     text: "Open..."
            //     shortcut: StandardKey.Open
            //     onTriggered: {
            //         fileDialog.open()
            //     }
            // }
            MenuItem {
                text: "about.*"
                onTriggered: signalShowAboutWindow()
            }
        }
    }

    // Action {
    //     id: aboutAction
    //     text: "New"
    //     shortcut: StandardKey.New
    //     onTriggered: console.log("new")
    // }

    toolBar: ToolBar {
        Button {
            id: btn1
            text: "Select All"
            anchors.verticalCenter: parent.verticalCenter
            onClicked: tableView.selection.selectAll()
        }

        Button {
            id: btnDownload
            text: "Download Selected PDFs"
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: btn1.right
            onClicked: {
                downloadFolderDialog.open()
            }
        }

        ToolBarSeparator {
            id: sep1
            anchors.left: btnDownload.right
        }

        Button {
            id: btnCheckLinks
            text: "Check Links"
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: sep1.right
            onClicked: {
                checkLinks()
            }
        }

        // TextField {
        //     id: searchBox
        //
        //     width: window.width / 5 * 2
        //     anchors.right: parent.right
        //     anchors.verticalCenter: parent.verticalCenter
        //
        //     placeholderText: "Search..."
        //     inputMethodHints: Qt.ImhNoPredictiveText
        //     onTextChanged: {
        //         console.log(searchBox.text)
        //     }
        // }
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
                text: "Status"
            }

            ProgressBar {
                id: statusProgressBar
                Layout.fillWidth: true
                Layout.minimumWidth: 150
                Layout.preferredWidth: 300
                visible: false
            }
        }
    }

    TableView {
        id: tableView
        objectName: "tableView"

        anchors.fill: parent

        Layout.minimumWidth: 400
        Layout.minimumHeight: 240
        Layout.preferredWidth: 600
        Layout.preferredHeight: 400

        frameVisible: false
        sortIndicatorVisible: true

        selectionMode: SelectionMode.ExtendedSelection

        property bool isKeyOReleased: true
        property var rowColors: { "-1": "magenta"}
        // property var rowColors: { 1: "magenta", 4: "blue", 5: "#00fbaa" }

        function openSelectedItems() {
            console.log("open selected items")
            tableView.selection.forEach(function(rowIndex) { openItem(rowIndex) })
        }

        function openItem(rowIndex) {
            var item = tableView.model.get(rowIndex)
            var refExtensionsToOpen = ["pdf", "url", "email"]

            var uri = item.ref;
            if (refExtensionsToOpen.indexOf(item.type) > -1) {
                if (item.type === "url" && uri.substr(0, 4) !== "http" && uri.substr(0, 7) !== "file://") {
                    uri = "http://" + uri
                }
                console.log("open item " + uri)
                Qt.openUrlExternally(uri)
            } else {
                console.log("onDoubleClicked: Cannot do anything with type " + item.type)
            }
        }

        Keys.onPressed: {
            // console.log("pressed key:", event.key, ", mod:", event.modifiers, ", text:", event.text, ", isAutoRepeat:", event.isAutoRepeat)
            if (event.text === "o" || event.key === 79) {
                if (tableView.isKeyOReleased) {
                    console.log("Open items by key")
                    tableView.isKeyOReleased = false
                    openSelectedItems()
                }
            } else if (event.text === "d" || event.key === 68) {
                if (tableView.isKeyOReleased) {
                    console.log("Download items via key")
                    tableView.isKeyOReleased = false
                    downloadFolderDialog.open()
                }
            }
        }

        Keys.onReleased: {
            // console.log("released", event.count, ", key:", event.key, ", mod:", event.modifiers, ", nativeScanCode:", event.nativeScanCode, ", text:", event.text, ", isAutoRepeat:", event.isAutoRepeat)
            //if (event.text === "o" || event.key === 79) {
                tableView.isKeyOReleased = true
            //}
        }

        Keys.onReturnPressed: {
            console.log("Open items by enter")
            openSelectedItems()
        }

        onDoubleClicked: {
            openItem(row)
        }

        itemDelegate: Item {
            clip: true
            Text {
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width
                leftPadding: 8
                topPadding: 2
                elide: styleData.elideMode
                color: {
                    // console.log("rowx", styleData.row)
                    // console.log("tableView.rowColors", styleData.row, tableView.rowColors[styleData.row])
                    return tableView.rowColors[styleData.row] || "#131313"
                }
                text: styleData.value
                renderType: Text.NativeRendering
            }
        }

        // rowDelegate: Rectangle {
        //     color: {
        //         // NEVER gets here after initial drawing
        //         console.log("tableView.rowColors", tableView.rowColors, tableView.rowColors["-1"], tableView.rowColors[1])
        //             if (tableView.rowColors[styleData.row]) {
        //                 console.log("rowDelegate: custom color ", tableView.rowColors[styleData.row], styleData.row)
        //                 color = tableView.rowColors[styleData.row]
        //             } else {
        //                 color = styleData.row % 2 ? "whitesmoke" : "white"
        //             }
        //         // }
        //     }
        //
        // }

        // style: TableViewStyle {
        //     highlightedTextColor: "pink"
        // }

        TableViewColumn {
            id: refColumn
            title: "Reference"
            role: "ref"
            movable: false
            resizable: true
            width: tableView.viewport.width - typeColumn.width - ((statusColumn.visible) ? statusColumn.width : 0)
        }

        TableViewColumn {
            id: typeColumn
            title: "Type"
            role: "type"
            movable: false
            resizable: true
            width: 80
        }

        TableViewColumn {
            id: statusColumn
            title: "Status"
            role: "status"
            movable: false
            resizable: true
            width: 120
            visible: false
        }
        //
        //
        // model: SortFilterProxyModel {
        //     id: proxyModel
        //     source: sourceModel.count > 0 ? sourceModel : null
        //
        //     sortOrder: tableView.sortIndicatorOrder
        //     sortCaseSensitivity: Qt.CaseInsensitive
        //     sortRole: sourceModel.count > 0 ?
        //               tableView.getColumn(tableView.sortIndicatorColumn).role : ""
        //
        //     filterString: "*" + searchBox.text + "*"
        //     filterSyntax: SortFilterProxyModel.Wildcard
        //     filterCaseSensitivity: Qt.CaseInsensitive
        // }

        // model: listModel
        model: ListModel {
            id: sourceModel
        }
    }

    FileDialog {
        id: downloadFolderDialog
        title: "Please choose an output folder"
        folder: shortcuts.home
        selectFolder: true
        onAccepted: {
            downloadFolderDialog.folder = downloadFolderDialog.fileUrls[0]
            startDownload(downloadFolderDialog.fileUrls[0])
        }
    }

    FileDialog {
        id: fileDialog
        title: "Choose a PDF document"
        folder: shortcuts.home
        selectMultiple: true
        nameFilters: [ "PDF document (*.pdf)", "All files (*)" ]
        onAccepted: {
            fileDialog.folder = fileDialog.fileUrls[0]
            SharedScripts.openPdfs(fileDialog.fileUrls, window.signalOpenPdfs)
        }
    }
}
