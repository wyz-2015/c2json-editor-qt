from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from common_widgets import *


class Enemies_Editor_Common(QWidget):
    def __init__(self):
        super(Enemies_Editor_Common, self).__init__()

        ##############################
        # 状态量
        self.dataBuffer = None

        self.widgets = {
            "health": Float_Line_Edit("血量"),
            "speed": Float_Line_Edit("移速"),
            "attack": Float_Line_Edit("伤害倍率(百分比)"),
            "desire": Float_Line_Edit("杀欲倍率(百分比)"),
            "size": Float_Line_Edit("精灵缩放倍率(百分比)")
        }

        ################################# 33########
        # 控件摆放
        v_layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()

        for paraName in ("health", "speed"):
            h_layout1.addWidget(self.widgets[paraName])

        for paraName in ("attack", "desire", "size"):
            h_layout2.addWidget(self.widgets[paraName])

        for layout in (h_layout1, h_layout2):
            v_layout.addLayout(layout)

        self.setLayout(v_layout)


if (__name__ == "__main__"):
    app = QApplication([])
    window = Enemies_Editor_Common()
    window.show()
    app.exec()
