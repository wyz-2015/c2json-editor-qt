from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import copy
from common_widgets import *


class Chars_Editor(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self):
        super(Chars_Editor, self).__init__()

        self.dataBuffer = None

        #################################################
        # 数据编辑区
        (self.groupBox_male, self.groupBox_female) = (QGroupBox(), QGroupBox())
        self.groupBox_male.setTitle("♂")
        self.groupBox_female.setTitle("♀")
        self.dataArea_male = Chars_Editor_Common(1)
        self.dataArea_female = Chars_Editor_Common(2)

        for dataArea in (self.dataArea_male, self.dataArea_female):
            dataArea.valueChanged.connect(self.update_data)
            dataArea.valueChanged.connect(self.valueChanged)

        layout_male = QHBoxLayout()
        layout_male.addWidget(self.dataArea_male)
        layout_female = QHBoxLayout()
        layout_female.addWidget(self.dataArea_female)

        self.groupBox_male.setLayout(layout_male)
        self.groupBox_female.setLayout(layout_female)

        ##########################################
        # 控件装入
        h_layout = QHBoxLayout()
        for i in (self.groupBox_male, self.groupBox_female):
            h_layout.addWidget(i)

        self.setLayout(h_layout)

    def set_data(self, PlayerData: dict):
        """
        载入数据进缓冲区。
        """
        self.dataBuffer = PlayerData
        for dataArea in (self.dataArea_male, self.dataArea_female):
            dataArea.set_data(self.dataBuffer)

    def get_data(self):
        """
        获取当前缓冲区数据的副本。
        """
        return self.dataBuffer

    def update_data(self):
        data = dict()
        for dataArea in (self.dataArea_male, self.dataArea_female):
            for (k, v) in dataArea.get_data().items():
                data[k] = v

        self.dataBuffer = data
        print(self.dataBuffer)


class Chars_Editor_Common(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, charId):
        super(Chars_Editor_Common, self).__init__()

        ##############################################
        # 状态信息
        self.charId = charId  # 角色编号，1男2女。
        self.dataBuffer = None
        self.existsUnlegalData = None
        #################################################

        # self.health = Float_Line_Edit("血量")
        # self.speed = Float_Line_Edit("移速")
        # self.jump = Float_Line_Edit("跳跃")
        # self.size = Float_Line_Edit("身体缩放(百分比)")
        # self.lives = Float_Line_Edit("命数")
        #
        # self.widgets = (
        #    self.health,
        #    self.speed,
        #    self.jump,
        #    self.size,
        #    self.lives
        # )

        self.widgets = {
            "player{0:n}_health".format(self.charId): Float_Line_Edit("血量"),
            "player{0:n}_speed".format(self.charId): Float_Line_Edit("移速"),
            "player{0:n}_jump".format(self.charId): Float_Line_Edit("跳跃"),
            "player{0:n}_size".format(self.charId): Float_Line_Edit("身体缩放(百分比)"),
            "player{0:n}_life".format(self.charId): Float_Line_Edit("命数")
        }
        # self.keysName = {
        #    "player{0:n}_health".format(self.charId),
        #    "player{0:n}_speed".format(self.charId),
        #    "player{0:n}_jump".format(self.charId),
        #    "player{0:n}_size".format(self.charId),
        #    "player{0:n}_life".format(self.charId)
        # }

        for widget in self.widgets.values():
            widget.valueChanged.connect(self.data_update)
            widget.valueChanged.connect(self.valueChanged)

        ################################
        # 控件摆放
        v_layout = QVBoxLayout()
        for widget in self.widgets.values():
            v_layout.addWidget(widget)

        self.setLayout(v_layout)

    def data_update(self):
        # data = {
        #    "player{0:n}_health".format(self.charId): self.health.get_value(),
        #    "player{0:n}_speed".format(self.charId): self.speed.get_value(),
        #    "player{0:n}_jump".format(self.charId): self.jump.get_value(),
        #    "player{0:n}_size".format(self.charId): self.size.get_value(),
        #    "player{0:n}_life".format(self.charId): self.lives.get_value()
        # }
        data = dict()
        for (name, widget) in self.widgets.items():
            data[name] = widget.get_value()

        self.dataBuffer = data
        self.existsUnlegalData = self.__check_legal__()
        # print(self.dataBuffer, self.existsUnlegalData)

    def set_data(self, PlayerData: dict):
        data = self.__data_filter__(PlayerData)
        self.dataBuffer = data
        print(self.dataBuffer)

        for (name, widget) in self.widgets.items():
            widget.set_value(self.dataBuffer[name])

    def get_data(self):
        return self.dataBuffer

    def __data_filter__(self, PlayerData):
        data = dict()
        for key in self.widgets:
            data[key] = PlayerData[key]

        return data

    def __check_legal__(self):
        value = 0
        for widget in self.widgets.values():
            value += int(widget.is_unlegal())

        return bool(value)


if (__name__ == "__main__"):
    app = QApplication([])
    window = Chars_Editor()
    window.show()
    app.exec()
