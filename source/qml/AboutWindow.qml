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

    title: "About PDFx"
    
    menuBar: MenuBar {
        Menu {
            title: "File"
            MenuItem {
                text: "Close Window"
                shortcut: StandardKey.Close
                onTriggered: {
                    window.close()
                }
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.rightMargin: 25
        Image {
            source: "../images/icon.png"
            fillMode: Image.PreserveAspectFit
        }
        Label {
            text: "<h1>PDFx</h1><p>v" + SharedScripts.__version__ + "</p><p><a href='https://www.metachris.com/pdfx'>Home Page</a></p><p><a href='https://github.com/metachris/pdfx-gui/issues'>Report a bug</a></p>"
            onLinkActivated: Qt.openUrlExternally(link)
            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.NoButton // we don't want to eat clicks on the Text
                cursorShape: parent.hoveredLink ? Qt.PointingHandCursor : Qt.ArrowCursor
            }
        }
    }
}
