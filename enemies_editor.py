from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from common_widgets import *
import json


class Enemies_Editor_Common(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, enemyMetaData={"name": "敌人代码名", "dest": "描述"}):
        super(Enemies_Editor_Common, self).__init__()

        ##############################
        # 状态量
        self.dataBuffer = None
        (self.enemyName, self.enemyDest) = (
            enemyMetaData["name"], enemyMetaData["dest"])
        self.existIllegalData = None

        self.widgets = {
            "health": Float_Line_Edit("血量"),
            "speed": Float_Line_Edit("移速"),
            "attack": Float_Line_Edit("伤害倍率(百分比)"),
            "desire": Float_Line_Edit("杀欲倍率(百分比)"),
            "size": Float_Line_Edit("精灵缩放倍率(百分比)")
        }

        ########################################
        # 槽信连接
        for widget in self.widgets.values():
            widget.valueChanged.connect(self.update_data)
            widget.valueChanged.connect(self.valueChanged)
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

        self.groupBox = QGroupBox(self.enemyDest)
        self.groupBox.setLayout(v_layout)

        temp_layout = QVBoxLayout()
        temp_layout.addWidget(self.groupBox)
        self.setLayout(temp_layout)

    def set_data(self, data):
        self.dataBuffer = data

        for (paraName, widget) in self.widgets.items():
            widget.set_value(self.dataBuffer[paraName])

        self.existIllegalData = False

    def get_data(self):
        return (self.enemyName, self.dataBuffer)

    def get_widgets(self):
        return self.widgets

    def update_data(self):
        data = {paraName: widget.get_value()
                for (paraName, widget) in self.widgets.items()}
        self.dataBuffer = data

        self.existIllegalData = self.__check_illegal__()

        print({self.enemyName: self.dataBuffer}, self.existIllegalData)

    def __check_illegal__(self):
        for widget in self.widgets.values():
            if (widget.is_illegal()):
                return True

        return False

    def get_existIllegalData(self):
        return self.existIllegalData


class Enemies_Editor(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self):
        super(Enemies_Editor, self).__init__()

        #######################################
        # 状态量
        self.dataBuffer = None
        self.existIllegalData = None

        self.enemiesList = self.__load_list__()
        self.__widgets_init__()

        self.scrollBar = QScrollArea()
        temp_widget = QWidget()
        temp_layout = QVBoxLayout()
        for enemy in self.enemiesList:
            temp_layout.addWidget(enemy["widget"])
        temp_widget.setLayout(temp_layout)
        self.scrollBar.setWidget(temp_widget)

        #####################################
        # 槽信连接
        for enemy in self.enemiesList:
            enemy["widget"].valueChanged.connect(self.update_data)
            enemy["widget"].valueChanged.connect(self.valueChanged)

        ############################################
        # 控件摆放
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.scrollBar)
        self.setLayout(v_layout)

    def __load_list__(self):
        """
        从json文件中读入代码名、俗名数据
        """
        with open("enemies.json", "rt", encoding="utf-8") as jsonfile:
            return json.load(jsonfile)

    def __widgets_init__(self):
        """
        将控件塞入形成的列表中
        """
        for enemy in self.enemiesList:
            enemy["widget"] = Enemies_Editor_Common(enemy)

    def __check_illegal__(self):
        for enemy in self.enemiesList:
            if (enemy["widget"].get_existIllegalData()):
                return True
        return False

    def update_data(self):
        widget = self.sender()
        (enemyName, data) = widget.get_data()
        self.dataBuffer[enemyName] = data

        self.existIllegalData = self.__check_illegal__()

    def set_data(self, data):
        self.dataBuffer = data

        for enemy in self.enemiesList:
            enemy["widget"].set_data(self.dataBuffer[enemy["name"]])

        self.existIllegalData = False

    def get_data(self):
        return self.dataBuffer

    def get_widgets(self):
        """
        [
            {"name": "enemyxx", "dest": "……", "widget": Enemies_Editor_Common()},
            {"name": "enemyxx", "dest": "……", "widget": Enemies_Editor_Common()},
            ...
        ]
        """
        return self.enemiesList

    def get_existIllegalData(self):
        return self.existIllegalData


if (__name__ == "__main__"):
    app = QApplication([])
    # window = Enemies_Editor_Common()
    window = Enemies_Editor()
    window.show()
    app.exec()
