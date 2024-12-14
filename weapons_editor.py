from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from common_widgets import *
import json


class Weapons_Nickname(QWidget):
    textChanged = pyqtSignal()

    def __init__(self, lbName):
        super(Weapons_Nickname, self).__init__()

        self.lb = QLabel(lbName)

        self.textEdit = QPlainTextEdit()
        self.textEdit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
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
        self.textEdit.setPlainText(text)
        self.textEdit.blockSignals(False)

    def get_text(self):
        return self.textEdit.toPlainText()


class Weapons_Editor_Common(QWidget):
    # 数据的输入、输出、更新(完成)
    valueChanged = pyqtSignal()

    def __init__(self, weaponMetaData={"name": "weaponxx", "dest": "(武器俗称)", "atk_types": 1}):
        super(Weapons_Editor_Common, self).__init__()

        #############################################
        # 状态量
        (self.weaponDest, self.weaponMetaName, self.numOfAtkTypes) = (
            weaponMetaData["dest"], weaponMetaData["name"], weaponMetaData["atk_types"])
        self.dataBuffer = None
        self.existIllegalData = None
        # self.setMinimumWidth(480)# 没有用？

        # self.lb = QLabel(weaponDest) #去最外层的QGroupBox再显示武器俗称
        self.groupBox = QGroupBox(self.weaponDest)  # 就在这里实现，试试

        self.widgets = {
            "name": Weapons_Nickname("自定昵称"),
            "lock": Float_Line_Edit("第几关解锁"),
            "magz": Float_Line_Edit("备弹数"),
            "freq": Float_Line_Edit("开火频率(百分比)"),
            "bult": Float_Line_Edit("单次开火弹幕数"),
            "sped": Float_Line_Edit("弹幕速度"),
            # "dmg1": Tuple_Float_Line_Edit(("单弹幕单伤", "单弹幕总伤"))
        }
        #####################
        # 攻击方式自动推导
        self.dmgs = ["dmg%d" % (n) for n in range(1, self.numOfAtkTypes + 1)]
        for dmg in self.dmgs:
            self.widgets[dmg] = Tuple_Float_Line_Edit(
                ("%s单弹幕单伤" % (dmg), "%s单弹幕总伤" % (dmg)))

        self.widgets["name"].textChanged.connect(self.update_data)
        self.widgets["name"].textChanged.connect(self.valueChanged)
        for key in (["lock", "magz", "freq", "bult", "sped"] + self.dmgs):
            # 一定要先update_data，再valueChanged ！！！！！！！
            self.widgets[key].valueChanged.connect(self.update_data)
            self.widgets[key].valueChanged.connect(self.valueChanged)

        ##############################################
        # 控件摆放
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()
        h_layout2_2 = QHBoxLayout()
        v_layout = QVBoxLayout()

        # h_layout1.addWidget(self.lb)
        v_layout.addWidget(self.widgets["name"])
        for key in ("lock", "magz", "freq"):
            h_layout2.addWidget(self.widgets[key])
        for key in ("bult", "sped"):  # , "dmg1"):
            h_layout2_2.addWidget(self.widgets[key])
        for layout in (h_layout2, h_layout2_2):
            v_layout.addLayout(layout)
        for dmg in self.dmgs:  # dmg自动推导
            v_layout.addWidget(self.widgets[dmg])
        h_layout1.addLayout(v_layout)

        self.groupBox.setLayout(h_layout1)

        layout4groupBox = QHBoxLayout()
        layout4groupBox.addWidget(self.groupBox)

        self.setLayout(layout4groupBox)

    def set_data(self, data):
        self.dataBuffer = data

        self.widgets["name"].set_text(self.dataBuffer["name"])
        for key in (["lock", "magz", "freq", "bult", "sped"] + self.dmgs):
            self.widgets[key].set_value(self.dataBuffer[key])

        self.existIllegalData = False

    def get_data(self):
        # 由于所有控件发送的信息，都一股脑地发送到上级控件同一个处理函数中，必须“包装”一个名字信息作区分。
        return (self.weaponMetaName, self.dataBuffer)

    def update_data(self):
        data = dict()
        data["name"] = self.widgets["name"].get_text()
        for key in (["lock", "magz", "freq", "bult", "sped"] + self.dmgs):
            data[key] = self.widgets[key].get_value()

        self.dataBuffer = data

        self.existIllegalData = self.__check_illegal__()

        print({self.weaponMetaName: self.dataBuffer}, self.existIllegalData)

    def get_widgets(self):
        return self.widgets

    def __check_illegal__(self):
        for key in (["lock", "magz", "freq", "bult", "sped"] + self.dmgs):
            if (self.widgets[key].is_illegal()):
                return True
        else:
            return False

    def get_existIllegalData(self):
        return self.existIllegalData


class Weapons_Editor(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self):
        super(Weapons_Editor, self).__init__()

        ########################################
        # 状态量
        # self.resize(800,60)
        # self.setMinimumHeight(600)
        self.dataBuffer = None
        self.existIllegalData = None

        self.weaponList = self.__load_list__()
        self.__widgets_init__()

        # print(self.weaponList)

        ########################################
        # 推导生成标签页样式
        self.tabWidget = QTabWidget()
        temp_pageName = 'A'
        for page in self.weaponList:
            temp_widget = QWidget()
            temp_scrollArea = QScrollArea()
            temp_v_layout = QVBoxLayout()
            for weapon in page:
                temp_v_layout.addWidget(weapon["widget"])
            temp_widget.setLayout(temp_v_layout)
            temp_scrollArea.setWidget(temp_widget)
            self.tabWidget.addTab(temp_scrollArea, temp_pageName)
            temp_pageName = chr(ord(temp_pageName)+1)

        ############################################
        # 槽信连接
        for page in self.weaponList:
            for weapon in page:
                weapon["widget"].valueChanged.connect(self.update_data)
                weapon["widget"].valueChanged.connect(self.valueChanged)

        ###########################################
        # 控件摆放
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.tabWidget)

        self.setLayout(v_layout)

    def __load_list__(self):
        """
        读取“weapon.json”文件，读入其中的武器分区表、俗名表
        """
        with open("weapons.json", "rt", encoding="utf-8") as jsonfile:
            return json.load(jsonfile)

    def __widgets_init__(self):
        """
        在self.weaponList中塞入控件
        """
        for page in self.weaponList:
            for item in page:
                item["widget"] = Weapons_Editor_Common(item)

    def __check_illegal__(self):
        for page in self.weaponList:
            for item in page:
                if (item["widget"].get_existIllegalData()):
                    return True
        else:
            return False

    ##########################################################
    # 槽函数区
    def update_data(self):
        widget = self.sender()
        (key, data) = widget.get_data()
        self.dataBuffer[key] = data

        # self.valueChanged.emit()
        self.existIllegalData = self.__check_illegal__()

    def set_data(self, data):
        self.dataBuffer = data

        for page in self.weaponList:
            for weapon in page:
                weapon["widget"].set_data(self.dataBuffer[weapon["name"]])

        self.existIllegalData = False

    def get_data(self):
        return self.dataBuffer

    def get_widgets(self):
        """
        [
            [
                {"name": "weaponxx", "dest": "……", "widget": Weapons_Editor_Common()},
                {"name": "weaponxx", "dest": "……", "widget": Weapons_Editor_Common()},
                ...
            ],
            [
                {"name": "weaponxx", "dest": "……", "widget": Weapons_Editor_Common()},
                {"name": "weaponxx", "dest": "……", "widget": Weapons_Editor_Common()},
                ...
            ],
            ...
        ]
        """
        return self.weaponList

    def get_existIllegalData(self):
        return self.existIllegalData


if (__name__ == "__main__"):
    app = QApplication([])
    # window = Weapons_Editor_Common()
    window = Weapons_Editor()
    window.show()
    app.exec()
