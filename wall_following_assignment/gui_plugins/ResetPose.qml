import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3

Rectangle {
  id: resetPose
  color: "transparent"
  anchors.fill: parent
  Layout.minimumWidth: 250
  Layout.minimumHeight: 90

  ColumnLayout {
    // Anchor to the top only, so the button and its status line stack
    // under the title bar instead of spreading over the card's height.
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: 10
    spacing: 6

    Button {
      Layout.fillWidth: true
      text: "Reset pose to start"
      font.capitalization: Font.MixedCase
      onClicked: ResetPose.OnReset()
      ToolTip.visible: hovered
      ToolTip.delay: 500
      ToolTip.text: "Teleport the robot back to where it spawned"
    }

    Label {
      Layout.fillWidth: true
      text: ResetPose.status
      wrapMode: Text.WordWrap
      font.pointSize: 9
      opacity: 0.7
    }
  }
}
