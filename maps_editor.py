import PyQt6
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from c2ir import IR


class FileIO_ToolBar(QToolBar):
    """
    文件IO。只是把画有东西ToolBar封装起来，功能实现不在这里。下同。
    """

    def __init__(self):
        super(FileIO_ToolBar, self).__init__()

        self.btn_loadFullIR = QPushButton("[<= 导入全部关卡数据")
        self.btn_loadIRPart = QPushButton("[<- 导入部分关卡数据")
        self.btn_writeFullIR = QPushButton("[=> 导出全部关卡数据")
        self.btn_writeIRPart = QPushButton("[-> 导出部分关卡数据")

        self.btns = (self.btn_loadFullIR, self.btn_loadIRPart,
                     self.btn_writeFullIR, self.btn_writeIRPart)

        for widget in self.btns:
            self.addWidget(widget)


class Base_ToolBar(QToolBar):
    """
    基本的对象添加、删除，等。
    """

    def __init__(self):
        super(Base_ToolBar, self).__init__()

        self.btn_addObj = QPushButton("[+] 添加对象")
        self.btn_deleteObj = QPushButton("[-] 删除(当前)对象")
        self.btn_moveObj = QPushButton("[->] 等效迁移(当前)对象")
        self.btn_cc = QPushButton("[|>] 地图编译并暂存")

        self.btns = (self.btn_addObj, self.btn_deleteObj,
                     self.btn_moveObj, self.btn_cc)

        for widget in self.btns:
            self.addWidget(widget)


class WaveManager_ToolBar(QToolBar):
    """
    波次管理器
    """

    def __init__(self):
        super(WaveManager_ToolBar, self).__init__()

        self.btn_setCurrentWave = QPushButton("设定关注波次")
        self.btn_ignoreWaves = QPushButton("显示所有对象")
        self.btn_setWaveRange = QPushButton("设定波次上限(无下限)")
        self.btn_insertWave = QPushButton("[^] 插入波")
        self.btn_deleteWave = QPushButton("[-] 删除波")

        self.btns = (self.btn_setCurrentWave, self.btn_setWaveRange, self.btn_ignoreWaves,
                     self.btn_insertWave, self.btn_deleteWave)

        for widget in self.btns:
            self.addWidget(widget)


class Obj_Explorer(QTreeWidget):
    """
    关卡对象资源管理器
    """

    def __init__(self, mapIR: dict = None):
        super(Obj_Explorer, self).__init__()
        self.mapIR = mapIR
        self.setHeaderLabels(("Level", "Stage", "对象"))
        self.setColumnCount(3)

        self.setColumnWidth(0, 80)
        self.setColumnWidth(1, 40)
        self.setColumnWidth(2, 50)

    def set_mapIR(self, mapIR: dict):
        self.mapIR = mapIR

    def tree_init(self):
        self.root = QTreeWidgetItem()
        self.root.setBackground(0, QBrush(Qt.GlobalColor.yellow))
        self.root.setBackground(1, QBrush(Qt.GlobalColor.green))

        for level in self.mapIR:
            child1 = QTreeWidgetItem((level, "", ""))
            self.root.addChild(child1)
            for stage in self.mapIR[level]:
                child2 = QTreeWidgetItem()
                child2.setText(1, stage)
                child1.addChild(child2)
        # TODO

        self.addTopLevelItem(self.root)
        # self.expandAll()


class Maps_Editor_Main_Widget(QMainWindow):
    valueChanged = pyqtSignal()

    def __init__(self):
        super(Maps_Editor_Main_Widget, self).__init__()

        ###################################
        # 变量或对象
        self.dataIR = IR()
        self.dataBuffer = None  # 名义上还叫作“dataBuffer”，实质上已经是东周天子，象征性需要，跟main.py交互需要。数据大权在楼上。
        self.currentStage = ['1', '1']  # 当前正在操作的区段
        self.currentObj = None  # 当前正在操作的对象

        ####################################
        # 工具栏
        self.fileIO_ToolBar = FileIO_ToolBar()
        self.base_ToolBar = Base_ToolBar()
        self.waveManager_ToolBar = WaveManager_ToolBar()
        for toolBar in (self.fileIO_ToolBar, self.base_ToolBar, self.waveManager_ToolBar):
            self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolBar)

        ####################################
        # 中央控件
        # TODO
        self.objExplorer = Obj_Explorer(
            self.dataIR.dataBuffer)  # TODO：需要修改，用函数修改数据，避免直接操作
        # print(self.dataIR.dataBuffer)
        self.obj2DViewer = QWidget()
        self.objParamsEditor = QWidget()

        self.objExplorer.tree_init()

        self.centerWidget = QWidget()  # 故意如此命名，规避重名
        h_layout = QHBoxLayout()
        for widget in (self.objExplorer, self.obj2DViewer, self.objParamsEditor):
            h_layout.addWidget(widget)
        self.centerWidget.setLayout(h_layout)
        self.setCentralWidget(self.centerWidget)

        ###################################
        # 按钮信号与功能函数连接
        # TODO

    #################################
    # 东周天子函数
    def get_data(self):
        return self.dataIR.get_json_dict()

    def set_data(self, LevelData: dict):
        self.dataIR.load_from_json_dict(LevelData)
        # TODO:应该需要一个当即刷新的函数

    ###########################################
    # 按钮功能函数
    # TODO


if (__name__ == "__main__"):
    app = QApplication([])
    window = Maps_Editor_Main_Widget()
    # window = Obj_Explorer()
    window.show()
    app.exec()
