from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

REPLACEMENT_VALUE = 0.1145141919810


class Float_Line_Edit_Core(QLineEdit):
    def __init__(self):  # , lbName="未命名参数"):
        super(Float_Line_Edit_Core, self).__init__()
        ############################
        # 状态变量
        self.existsIllegalValue = True

        # self.lb1 = QLabel(lbName) #QLabel也需要分离出去，提高代码复用

        self.setObjectName("lineEdit")
        self.setPlaceholderText("尚未输入数值……")
        self.textChanged.connect(self.value_check)

        ##########################
        # 控件摆放，但是由于只有一个控件，所以不需要了
        # h_layout = QHBoxLayout()
        # for item in (self.lb1, self.lineEdit):
        #    h_layout.addWidget(item)
        # h_layout.addWidget(self.lineEdit)

        # self.setLayout(h_layout)

    def set_value(self, value):
        self.blockSignals(True)  # 设置值时不引发textChanged事件
        self.setText(str(value))
        self.blockSignals(False)

        self.existsIllegalValue = False  # 默认传入的不会是有问题的值。

    def get_value(self):
        value = self.text()

        # 区分整数和小数
        value = float(value)
        if (value == int(value)):
            return int(value)
        else:
            return value

    def value_check(self):
        """
        确认当前编辑栏中的数值是否为合法的数值。
        """
        value = self.text()
        try:
            float(value)
            self.existsIllegalValue = False
        except:
            self.existsIllegalValue = True

        if (self.existsIllegalValue):
            self.setStyleSheet("QLineEdit#lineEdit { color: red; }")
        else:
            self.setStyleSheet(
                "QLineEdit#lineEdit { color: black; }")

    def is_illegal(self) -> bool:
        return self.existsIllegalValue


class Float_Line_Edit(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, lbName="未命名参数"):
        super(Float_Line_Edit, self).__init__()

        self.lb = QLabel(lbName)
        self.floatLineEdit = Float_Line_Edit_Core()

        self.floatLineEdit.textChanged.connect(self.valueChanged)  # 数值改变信号连接。

        #####################################
        # 控件摆放
        h_layout = QHBoxLayout()
        for widget in (self.lb, self.floatLineEdit):
            h_layout.addWidget(widget)

        self.setLayout(h_layout)

    def set_value(self, value):
        self.floatLineEdit.set_value(value)

    def get_value(self):
        # try:
        #    return self.floatLineEdit.get_value()
        # except:
        #    QMessageBox.warning(
        #        self, "错误数据", "“{0:s}”中填入的数据不是有效的整数或小数。".format(self.lb.text()), QMessageBox.Ok)
        if (self.floatLineEdit.is_illegal()):
            print("“{0:s}”中填入的数据不是有效的整数或小数，在数据缓冲区中已暂时用“{1}”替代。".format(
                self.lb.text(), REPLACEMENT_VALUE))
            # return None
            return REPLACEMENT_VALUE
        else:
            return self.floatLineEdit.get_value()

    def is_illegal(self):
        return self.floatLineEdit.is_illegal()


class Choose_One(QWidget):
    # 我是SB！这种单选的小事，并且没有魔改的可能或必要，用得着我一个第三方实现吗？
    # 删了可惜，就这么留着，如有必要随时可以改改就用。

    choiceChanged = pyqtSignal()

    def __init__(self, lbName: str, choices: dict):
        """
        choices:
        {结果代码: 外显的说明字符串}
        例如：{False: "关闭", True: "开启"}
        """
        super(Choose_One, self).__init__()

        #########################################
        # 当前状态
        self.currentChoice = None
        ##########################################

        self.lb = QLabel(lbName)

        self.choices = choices
        self.radioBtns = {choice: QRadioButton(description) for (
            choice, description) in self.choices.items()}

        for (_choice, radioBtn) in self.radioBtns.items():
            radioBtn.toggled.connect(self.choiceChanged)
            radioBtn.toggled.connect(self.change_choice(_choice))

        #############################################
        # 控件摆放
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.lb)

        for radioBtn in self.radioBtns.values():
            h_layout.addWidget(radioBtn)

        self.setLayout(h_layout)

    def change_choice(self, _choice):
        # 本来用lambda函数实现，但是会导致所有的选项都只跟最后一个choice关联，只能这么“绕圈”实现。
        def f():
            self.currentChoice = _choice
            print(self.currentChoice)

        return f

    def set_choice(self, choice):
        self.currentChoice = choice

        self.radioBtns[choice].blockSignals(True)
        self.radioBtns[choice].setChecked(True)
        self.radioBtns[choice].blockSignals(False)

    def get_choice(self):
        return self.currentChoice


class Tuple_Float_Line_Edit(QWidget):
    """
    paraNames:
    其中元素均为str的可迭代对象。
    例如：("x", "y", "z"), ["114", "514"]
    """

    valueChanged = pyqtSignal()

    def __init__(self, paraNames):
        super(Tuple_Float_Line_Edit, self).__init__()

        self.paraNames = paraNames

        lb1_text = "({0:s})=(".format(",".join(self.paraNames))
        self.lb1 = QLabel(lb1_text)
        self.lb2 = QLabel(")")

        self.floatLineEdits = {paraName: Float_Line_Edit_Core()
                               for paraName in self.paraNames}
        for widget in self.floatLineEdits.values():
            widget.textChanged.connect(self.valueChanged)

        ###################################################
        # 控件摆放
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.lb1)
        for widget in self.floatLineEdits.values():
            h_layout.addWidget(widget)
        h_layout.addWidget(self.lb2)

        self.setLayout(h_layout)

    def set_value(self, values):
        """
        values:
        2种可用类型：(1)dict (2)其他可迭代类型，tuple、list等
        """
        if (type(values) == type(dict())):
            # 允许2种设值方式，一种通过字典匹配键名设值。好处是允许部分改值
            for (k, v) in values.items():
                self.floatLineEdits[k].set_value(v)
        else:
            # 另一种方式则是按实例化本类时的参数名列表的顺序，依次赋值。
            for i in range(len(self.paraNames)):
                self.floatLineEdits[self.paraNames[i]].set_value(values[i])

    def get_value(self, returnType=None):
        """
        returnType:
        如果填dict，则数据会以{传入时的参数名: 值}的形式返回。
        """
        values = [(self.floatLineEdits[paraName].get_value() if (
            not self.floatLineEdits[paraName].is_illegal()) else REPLACEMENT_VALUE) for paraName in self.paraNames]

        if (returnType == dict):
            values2 = dict()
            for i in range(len(self.paraNames)):
                values2[self.paraNames[i]] = values[i]
            return values2
        else:
            return values

    def is_illegal(self):
        for paraName in self.paraNames:
            if(self.floatLineEdits[paraName].is_illegal()):
                return True
        else:
            return False


if (__name__ == "__main__"):
    app = QApplication([])
    # window = Float_Line_Edit()
    # window = Choose_One(
    #    "114514", {"对的": "yyyyyyyyyyy", "不对！": "nnnnnnnnnnnnnnnnnnnnnnnn", 3: "ddddd"})
    window = Tuple_Float_Line_Edit(["114", "51444"])
    window.show()
    app.exec()
