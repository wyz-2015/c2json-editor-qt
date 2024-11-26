from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from common_widgets import *


class Meta_Data_Editor(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self):
        super(Meta_Data_Editor, self).__init__()

        ################################
        # 状态量
        self.dataBuffer = None
        #####################################

        self.lbText = '<span style="text-align: center;">由于模式选择、是否提前解锁所有关卡、是否允许作弊，都是选择性的。</span><br/><span style="text-align: center;">并不需要通过此第三方编辑器来实现填入非常规数据。</span><br/><span style="color: red; text-align: center;">故这几个选项，请回到作为mod制作必经之路的官方编辑器处进行修改。</span>'
        self.lb = QLabel(self.lbText)
        self.lb.setAlignment(Qt.AlignCenter)

        self.widgets = {
            "FrameRate": Float_Line_Edit("帧速率"),
            "VersionNumber": Float_Line_Edit("版本号")
        }

        for widget in self.widgets.values():
            widget.valueChanged.connect(self.valueChanged)
            widget.valueChanged.connect(self.update_data)

        ##################################################
        # 控件摆放
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.lb)
        for widget in self.widgets.values():
            v_layout.addWidget(widget)

        self.setLayout(v_layout)

    def set_data(self, data):
        self.dataBuffer = data

        for (name, widget) in self.widgets.items():
            widget.blockSignals(True)
            widget.set_value(self.dataBuffer[name])
            widget.blockSignals(False)

    def get_data(self):
        return self.dataBuffer

    def update_data(self):
        # 目前设计里，修改的数据只是传入数据的子集。故无法先本地制造数据dict再行替换，只能直接修改。坏处是无法单独调试本模块，除非传入一块完整的OtherData。
        for (name, widget) in self.widgets.items():
            self.dataBuffer[name] = widget.get_value()
        print(self.dataBuffer)

    def get_widgets(self):
        """
        {"键名": Float_Line_Edit()}
        """
        return self.widgets


if (__name__ == "__main__"):
    app = QApplication([])
    window = Meta_Data_Editor()
    window.show()
    app.exec()
