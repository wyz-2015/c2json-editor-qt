from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Float_Line_Edit_Core(QLineEdit):
    def __init__(self):  # , lbName="未命名参数"):
        super(Float_Line_Edit_Core, self).__init__()
        ############################
        # 状态变量
        self.existsUnlegalValue = True

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
        self.blockSignals(True) #设置值时不引发textChanged事件
        self.setText(str(value))
        self.blockSignals(False)
        
        self.existsUnlegalValue = False  # 默认传入的不会是有问题的值。

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
            self.existsUnlegalValue = False
        except:
            self.existsUnlegalValue = True

        if (self.existsUnlegalValue):
            self.setStyleSheet("QLineEdit#lineEdit { color: red; }")
        else:
            self.setStyleSheet(
                "QLineEdit#lineEdit { color: black; }")

    def is_unlegal(self) -> bool:
        return self.existsUnlegalValue


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
        if (self.floatLineEdit.is_unlegal()):
            print("“{0:s}”中填入的数据不是有效的整数或小数。".format(self.lb.text()))
            return None
        else:
            return self.floatLineEdit.get_value()

    def is_unlegal(self):
        return self.floatLineEdit.is_unlegal()


if (__name__ == "__main__"):
    app = QApplication([])
    window = Float_Line_Edit()
    window.show()
    app.exec()
