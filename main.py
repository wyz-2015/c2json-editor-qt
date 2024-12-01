from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import json
import pathlib
from characters_editor import Chars_Editor
from meta_data import Meta_Data_Editor
from weapons_editor import Weapons_Editor
from enemies_editor import Enemies_Editor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ###################################################
        # 状态变量
        # self.resize(1366, 768)
        self.resize(1080, 810)
        self.title = "Commando 2 创意工坊mod数据编辑器(Qt5)"
        self.setWindowTitle(self.title)
        self.currentFile = None  # type: pathlib.Path()
        self.currentDir = pathlib.Path().home()
        self.dataBuffer = None
        self.saved = None

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
        self.enemiesEditor=Enemies_Editor()
        self.enemiesEditor.valueChanged.connect(self.update_data)

        ###############################################
        # 元数据编辑
        self.metaDataEditor = Meta_Data_Editor()
        self.metaDataEditor.valueChanged.connect(self.update_data)

        ####################################################
        # 标签栏
        self.tabWidget = QTabWidget()
        self.tabWidget.setEnabled(False)#一开始不能使用，载入了文件才能使用。
        self.tabWidget.setTabPosition(QTabWidget.North)

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

            # 各部分控件载入数据
            self.charsEditor.set_data(self.dataBuffer["PlayerData"])
            self.metaDataEditor.set_data(self.dataBuffer["OtherData"])
            self.weaponsEditor.set_data(self.dataBuffer["WeaponData"])
            self.enemiesEditor.set_data(self.dataBuffer["EnemyData"])

            # 不载入文件不让使用保存功能
            self.set_data_saved(True)
            if (not (self.btn_save.isEnabled() and self.btn_save_as.isEnabled())):
                self.btn_save.setEnabled(True)
                self.btn_save_as.setEnabled(True)

            # 不载入文件不让使用
            self.tabWidget.setEnabled(True)

    def func_btn_save_as(self):
        (savePath, filter) = QFileDialog.getSaveFileName(
            self, "另存 .json 文件", str(self.currentDir), "(*.json)")
        if (savePath):
            print(self.dataBuffer)
            with open(savePath, "wt", encoding="utf-8") as jsonfile:
                json.dump(self.dataBuffer, jsonfile,
                          ensure_ascii=False, indent="\t")

            self.change_current_file(savePath)
            self.set_data_saved(True)

    def func_btn_save(self):
        if (not self.saved):
            print(self.dataBuffer)
            with open(str(self.currentFile), "wt", encoding="utf-8") as jsonfile:
                json.dump(self.dataBuffer, jsonfile,
                          ensure_ascii=False, indent="\t")

            self.set_data_saved(True)

    #######################################
    # 重写函数区
    def closeEvent(self, event):
        if (self.saved == False):
            # saved值为None(尚未载入文件)时，也不必提示是否需要保存，直接关闭即可。
            choice = QMessageBox.question(
                self, "文件尚未保存！", "是否保存了文件再退出？", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            match choice:
                case QMessageBox.Yes:
                    self.func_btn_save()
                    event.accept()
                case QMessageBox.No:
                    event.accept()
                case _:
                    event.ignore()
    ##################################

    def update_data(self):
        # 意想不到的收获：未载入文件时，dataBuffer为空，此行无法完成，于是无法执行最底下一行的程序。但是又不导致程序退出。
        self.dataBuffer["PlayerData"] = self.charsEditor.get_data()
        self.dataBuffer["OtherData"] = self.metaDataEditor.get_data()
        self.dataBuffer["WeaponData"] = self.weaponsEditor.get_data()
        self.dataBuffer["EnemyData"] = self.enemiesEditor.get_data()
        self.set_data_saved(False)

    def set_data_saved(self, b: bool):
        self.saved = b

        if (self.saved):
            self.setWindowTitle(str(self.currentFile))
        else:
            self.setWindowTitle(str(self.currentFile) + "*")  # 未保存标记

    def change_current_file(self, filePath: str):
        self.currentFile = pathlib.Path(filePath)
        self.currentDir = self.currentFile.parent

    ##################################


# def read_json_data(filePath: str):
#    with open(filePath, "rt") as jsonfile:
#        return json.load(jsonfile)


if (__name__ == "__main__"):
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
