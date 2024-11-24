from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from common_widgets import *


class Weapons_Nickname(QWidget):
    textChanged = pyqtSignal()

    def __init__(self, lbName):
        super(Weapons_Nickname, self).__init__()

        self.lb = QLabel(lbName)

        self.textEdit = QTextEdit()
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.textEdit.setFixedHeight(50)
        self.textEdit.textChanged.connect(self.textChanged)

        ######################################
        # 控件摆放
        h_layout = QHBoxLayout()
        for widget in (self.lb, self.textEdit):
            h_layout.addWidget(widget)

        self.setLayout(h_layout)

    def set_text(self, text: str):
        self.textEdit.blockSignals(True)
        self.textEdit.setText(text)
        self.textEdit.blockSignals(False)

    def get_text(self):
        return self.textEdit.toPlainText()


class Weapons_Editor_Common(QWidget):
    # TODO:数据的输入、输出、更新
    valueChanged = pyqtSignal()

    def __init__(self):  # weaponDest="(武器俗称)"):
        super(Weapons_Editor_Common, self).__init__()

        #############################################
        # 状态量
        self.dataBuffer = None

        # self.lb = QLabel(weaponDest) #去最外层的QGroupBox再显示武器俗称

        self.widgets = {
            "name": Weapons_Nickname("自定昵称"),
            "lock": Float_Line_Edit("第几关解锁"),
            "magz": Float_Line_Edit("备弹数"),
            "freq": Float_Line_Edit("开火频率(百分比)"),
            "bult": Float_Line_Edit("单次开火弹幕数"),
            "sped": Float_Line_Edit("弹幕速度"),
            "dmg1": Tuple_Float_Line_Edit(("单弹幕单伤", "单弹幕总伤"))
        }
        self.widgets["name"].textChanged.connect(self.valueChanged)
        self.widgets["name"].textChanged.connect(self.update_data)
        for key in ("lock", "magz", "freq", "bult", "sped", "dmg1"):
            self.widgets[key].valueChanged.connect(self.valueChanged)
            self.widgets[key].valueChanged.connect(self.update_data)

        ##############################################
        # 控件摆放
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()
        v_layout = QVBoxLayout()

        # h_layout1.addWidget(self.lb)
        v_layout.addWidget(self.widgets["name"])
        for key in ("lock", "magz", "freq", "bult", "sped", "dmg1"):
            h_layout2.addWidget(self.widgets[key])
        v_layout.addLayout(h_layout2)
        h_layout1.addLayout(v_layout)

        self.setLayout(h_layout1)

    def set_data(self, data):
        self.dataBuffer = data

        self.widgets["name"].set_text(self.dataBuffer["text"])
        for key in ("lock", "magz", "freq", "bult", "sped", "dmg1"):
            self.widget[key].set_value(self.dataBuffer[key])

    def get_data(self):
        return self.dataBuffer

    def update_data(self):
        data = dict()
        data["name"] = self.widgets["name"].get_text()
        for key in ("lock", "magz", "freq", "bult", "sped", "dmg1"):
            data[key] = self.widgets[key].get_value()

        self.dataBuffer = data
        print(self.dataBuffer)


class Weapons_Editor(QWidget):
    def __init__(self):
        super(Weapons_Editor, self).__init__()

        pass


if (__name__ == "__main__"):
    app = QApplication([])
    window = Weapons_Editor_Common()
    window.show()
    app.exec()
