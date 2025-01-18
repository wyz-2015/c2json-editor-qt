from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys
import json
import pathlib
from characters_editor import Chars_Editor
from meta_data import Meta_Data_Editor
from weapons_editor import Weapons_Editor
from enemies_editor import Enemies_Editor
from common_widgets import REPLACEMENT_VALUE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ###################################################
        # 状态变量
        # self.resize(1366, 768)
        self.resize(1080, 810)
        self.title = "Commando 2 创意工坊mod数据编辑器(Qt6)"
        self.setWindowTitle(self.title)
        self.currentFile = None  # type: pathlib.Path()
        self.currentDir = pathlib.Path().home()
        self.dataBuffer = None
        self.saved = None
        self.existIllegalData = None

        ################################################
        # 工具栏
        self.toolbar1 = QToolBar()

        self.btn_open = QPushButton("打开")
        self.btn_save = QPushButton("保存")
        self.btn_save_as = QPushButton("另存")

        for btn in (self.btn_open, self.btn_save, self.btn_save_as):
            self.toolbar1.addWidget(btn)

        for btn in (self.btn_save_as, self.btn_save):
            btn.setEnabled(False)

        self.btn_open.clicked.connect(self.func_btn_open)
        self.btn_save_as.clicked.connect(self.func_btn_save_as)
        self.btn_save.clicked.connect(self.func_btn_save)

        ###############################################
        # 操控人物编辑
        self.charsEditor = Chars_Editor()
        self.charsEditor.valueChanged.connect(self.update_data)

        ##############################################
        # 武器数据编辑
        self.weaponsEditor = Weapons_Editor()
        self.weaponsEditor.valueChanged.connect(self.update_data)

        ##############################################
        # 敌人数据编辑
        self.enemiesEditor = Enemies_Editor()
        self.enemiesEditor.valueChanged.connect(self.update_data)

        ###############################################
        # 元数据编辑
        self.metaDataEditor = Meta_Data_Editor()
        self.metaDataEditor.valueChanged.connect(self.update_data)

        ####################################################
        # 标签栏
        self.tabWidget = QTabWidget()
        self.tabWidget.setEnabled(False)  # 一开始不能使用，载入了文件才能使用。
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)

        # self.charsEditor_title="操控人物数据(PlayerData)"
        self.tabWidget.addTab(self.charsEditor, "操控人物数据(PlayerData)")
        self.tabWidget.addTab(self.weaponsEditor, "武器数据(WeaponData)")
        self.tabWidget.addTab(self.enemiesEditor, "敌方单位数据(EnemyData)")
        self.tabWidget.addTab(self.metaDataEditor, "有编辑意义的元数据(均来自OtherData)")

        ###################################################
        # 控件装入
        self.addToolBar(self.toolbar1)
        self.setCentralWidget(self.tabWidget)

    ###################################
    # 工具栏按钮函数
    def func_btn_open(self):
        (filePath, filter) = QFileDialog.getOpenFileName(
            self, "打开 .json 文件", str(self.currentDir), "(*.json)")
        if (filePath):
            print(filePath)
            self.change_current_file(filePath)
            # self.dataBuffer = read_json_data(filePath)
            with open(filePath, "rt", encoding="utf-8") as jsonfile:
                self.dataBuffer = json.load(jsonfile)

            self.set_data(self.dataBuffer)

            # 不载入文件不让使用保存功能
            self.set_data_saved(True)
            if (not (self.btn_save.isEnabled() and self.btn_save_as.isEnabled())):
                self.btn_save.setEnabled(True)
                self.btn_save_as.setEnabled(True)

            # 不载入文件不让使用
            self.tabWidget.setEnabled(True)

            # 默认一开始所有数据都是合法的
            self.existIllegalData = False

    def func_btn_save_as(self):
        if (self.existIllegalData):
            if (not self.__illegal_data_warning__(True)):  # 非法数据检查警告
                return -1  # 被中途中止

        (savePath, filter) = QFileDialog.getSaveFileName(
            self, "另存 *.json 文件", str(self.currentDir), "(*.json)")
        if (savePath):
            print(self.dataBuffer)
            with open(savePath, "wt", encoding="utf-8") as jsonfile:
                json.dump(self.dataBuffer, jsonfile,
                          ensure_ascii=False, indent="\t", sort_keys=True)

            self.change_current_file(savePath)
            self.set_data_saved(True)

    def func_btn_save(self):
        if (not self.saved):
            if (self.existIllegalData):
                if (not self.__illegal_data_warning__(True)):  # 非法数据检查警告
                    return -1  # 被中途中止

            print(self.dataBuffer)
            with open(str(self.currentFile), "wt", encoding="utf-8") as jsonfile:
                json.dump(self.dataBuffer, jsonfile,
                          ensure_ascii=False, indent="\t", sort_keys=True)

            self.set_data_saved(True)

    #######################################
    # 重写函数区
    def closeEvent(self, event):
        if (self.saved == False):
            # saved值为None(尚未载入文件)时，也不必提示是否需要保存，直接关闭即可。
            choice = QMessageBox.question(
                self, "文件尚未保存！", "是否保存了文件再退出？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            match choice:
                case QMessageBox.StandardButton.Yes:
                    if (self.func_btn_save() == -1):
                        event.ignore()
                    else:
                        event.accept()
                case QMessageBox.StandardButton.No:
                    event.accept()
                case _:
                    event.ignore()
    ##################################

    def update_data(self):
        # 意想不到的收获：未载入文件时，dataBuffer为空，此行无法完成，于是无法执行最底下一行的程序。但是又不导致程序退出。Windows: sodayo
        self.dataBuffer["PlayerData"] = self.charsEditor.get_data()
        self.dataBuffer["OtherData"] = self.metaDataEditor.get_data()
        self.dataBuffer["WeaponData"] = self.weaponsEditor.get_data()
        self.dataBuffer["EnemyData"] = self.enemiesEditor.get_data()

        self.set_data_saved(False)
        self.existIllegalData = self.__check_illegal__()
        print(self.existIllegalData)

    def set_data(self, data):
        # 各部分控件载入数据
        self.charsEditor.set_data(self.dataBuffer["PlayerData"])
        self.metaDataEditor.set_data(self.dataBuffer["OtherData"])
        self.weaponsEditor.set_data(self.dataBuffer["WeaponData"])
        self.enemiesEditor.set_data(self.dataBuffer["EnemyData"])

        self.existIllegalData = False  # 自动补充的数据不是非法数据，所以直接设定为没有非法数据了。

    def __check_illegal__(self):
        for module in (self.charsEditor, self.metaDataEditor, self.weaponsEditor, self.enemiesEditor):
            if (module.get_existIllegalData()):
                return True
        else:
            return False

    def set_data_saved(self, b: bool):
        self.saved = b

        if (self.saved):
            self.setWindowTitle(str(self.currentFile))
        else:
            self.setWindowTitle(str(self.currentFile) + "*")  # 未保存标记

    def change_current_file(self, filePath: str):
        self.currentFile = pathlib.Path(filePath)
        self.currentDir = self.currentFile.parent

    def __illegal_data_warning__(self, q=False) -> bool:
        """
        q: 是否是询问模式
        True: 询问模式，询问是否继续
        False: 纯弹出警告信息
        """
        self.set_data(self.dataBuffer)

        (q_message, q_choice) = (None, None)
        if (q):
            # q_message = "\n如果您选择“继续”，则意味着您采用了本程序帮您自动补上的数据，随之，整份数据也确实“正确”了。\n是否继续？"
            q_message = "是否继续？"
            q_choice = (QMessageBox.StandardButton.Yes |
                        QMessageBox.StandardButton.No)
        else:
            q_message = ""
            q_choice = QMessageBox.StandardButton.Yes

        choice = QMessageBox.warning(self, "警告：存在不正确数据", "您在本份数据的某处，填入了不正确的数据。\n无论如何，至少数据的数字应该∈ℝ。\n已为您暂时将不正确的数据替换为：{0}，只是为了提醒您作出修改。随之，您的数据现在已暂时“正确“。{1:s}".format(
            REPLACEMENT_VALUE, q_message), q_choice)
        match choice:
            case QMessageBox.StandardButton.Yes:
                return True
            case QMessageBox.StandardButton.No:
                return False

    ##################################


# def read_json_data(filePath: str):
#    with open(filePath, "rt") as jsonfile:
#        return json.load(jsonfile)


if (__name__ == "__main__"):
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
