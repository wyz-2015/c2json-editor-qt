import PyQt6
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree
from c2ir import IR
import pathlib


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
        self.btn_ignoreWaves = QPushButton("[*_*] 显示所有对象")
        self.btn_viewWave = QPushButton("[*_-] 只显示关注波次的单位")
        self.btn_setWaveRange = QPushButton("设定波次上限(无下限)")  # deleted
        self.btn_insertWave = QPushButton("[^] 插入波")
        self.btn_deleteWave = QPushButton("[-] 删除波")

        self.btns = (self.btn_setCurrentWave,  self.btn_viewWave, self.btn_ignoreWaves,
                     self.btn_insertWave, self.btn_deleteWave)

        for widget in self.btns:
            self.addWidget(widget)


class Obj_Explorer(QTreeWidget):
    """
    关卡对象资源管理器
    """
    objWasSelected = pyqtSignal(int)

    def __init__(self):  # , mapIR_main: dict = None):
        super(Obj_Explorer, self).__init__()
        self.mapIR_main = None
        self.mapIR_bin = None
        self.setHeaderLabels(("Level-Stage", "对象数", "对象ID", "对象描述"))
        self.setColumnCount(4)

        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 40)
        self.setColumnWidth(2, 40)
        self.setColumnWidth(3, 50)

        self.itemActivated.connect(self.emit_selected_id)

    def set_mapIR(self, mapIR_main: dict, mapIR_bin: dict):
        self.mapIR_main = mapIR_main
        self.mapIR_bin = mapIR_bin
        self.tree_init()

    def tree_init(self):
        """
        初始化树视图
        """
        self.clear()

        self.root = QTreeWidgetItem()
        self.root.setText(0, "现有对象")
        # self.root.setBackground(0, QBrush(Qt.GlobalColor.yellow))
        self.root.setBackground(0, QBrush(Qt.GlobalColor.green))

        for level in self.mapIR_main:
            # child1 = QTreeWidgetItem((level, "", ""))
            child1 = QTreeWidgetItem()
            child1.setText(0, level)
            self.root.addChild(child1)
            for stage in self.mapIR_main[level]:
                child2 = QTreeWidgetItem()
                child2.setText(0, stage)
                child2.setText(1, "{0:n}".format(
                    len(self.mapIR_main[level][stage]["objects"] + self.mapIR_main[level][stage]["locks"])))

                for obj in (self.mapIR_main[level][stage]["objects"] + self.mapIR_main[level][stage]["locks"]):
                    child3 = QTreeWidgetItem()
                    child3.setText(2, str(obj["id"]))
                    child3.setText(3, obj["dest"])
                    # child3.setHidden(True)

                    child2.addChild(child3)

                child1.addChild(child2)

        self.addTopLevelItem(self.root)
        # self.expandAll()

        #################################
        # 回收站
        self.bin = QTreeWidgetItem()
        self.bin.setText(0, "对象回收站")
        self.bin.setBackground(0, QBrush(Qt.GlobalColor.red))
        self.bin.setText(1, "{0:n}".format(len(self.mapIR_bin)))
        for obj in self.mapIR_bin:
            child1 = QTreeWidgetItem(("", "", str(obj["id"]), obj["dest"]))
            self.bin.addChild(child1)

        self.addTopLevelItem(self.bin)

        # TODO:能加入对树上事物的增减移动操作吗？——目前考虑：以缪塔丽的mod作为样本，重绘树函数的时间在0.007s左右，故目前考虑直接以重绘的方式实现刷新。

    def emit_selected_id(self, item, column):
        """
        当对象被选中时，返回对象id
        """
        _id = item.text(2)
        if (_id):
            self.objWasSelected.emit(int(_id))


class Obj_ParamsEditor(QWidget):
    def __init__(self):
        super(Obj_ParamsEditor, self).__init__()

    def __build_params_tree_4_use__(self, objIR: dict) -> dict:
        rootName = "{0:s} :: {1:s}".format(objIR["name"], objIR["dest"])
        root = {"name": rootName, "type": "group", "children": []}

        ##################################
        # 需要单独处理的：坐标
        (x, y) = objIR["pos"]
        posGroup_x = {"name": "x=", "type": "float", "value": x}
        posGroup_y = {"name": "y=", "type": "float", "value": y}
        for i in (posGroup_x, posGroup_y):
            root["children"].append(i)

        not2Phase = ("name", "dest", "rem", "pos")
        for (k, v) in objIR.items():
            if (not (k in not2Phase)):
                if ("varNameList" in v):  # 如果是特殊参数列表
                    param = {"name": "{0:s} :: ".format(
                        k), "type": "group", "children": []}
                    paramChildren = param["children"]

                    for k_sub in v["varNameList"]:
                        subNode = {
                            "name": ""
                        }
                        # TODO
                else:  # 普通参数
                    self.__build_params_tree_4_use_DFS1__(
                        k, v, root["children"])

    def __find_valuesSet_and_value__(self, _d: dict):
        """
        可能返回一个tuple或0，0代表未找到，意味着需要往下递归。
        """
        for k in _d:
            if (_d.endswith("_current")):
                return (k.removesuffix("_current"), k)

        return 0

    def __build_params_tree_4_use_DFS1__(self, obj_k, obj_v, parentNode: list):
        """
        递归处理遇到的普通参数
        """
        tryFindKV = self.__find_valuesSet_and_value__(obj_v)
        if (tryFindKV):  # 可以找到值，则生成参数结点
            (k_Vset, k_Vcurrent) = tryFindKV
            if (k_Vset == -32768):
                param = {"name": "{0:s} :: {1:s}".format(k, v["dest"]),
                         "type": "float",
                         "value": v[k_Vcurrent]}
            elif (type(k_Vset) == type(dict())):
                param = {
                    "name": "{0:s} :: {1:s}".format(k, v["dest"]),
                    "type": "list",
                    "value": v[k_Vcurrent]
                    "limits": self.__vSet_convert__(v[k_Vset])
                }
            parentNode.append(param)
        else:  # 在此节点找不到值，则向下递归
            subNode = {
                "name": "{0:s} :: ".format(obj_k),
                "type": "group",
                "children": []
            }
            parentNode.append(subNode)
            for (k_sub, v_sub) in obj_v.items():
                self.__build_params_tree_4_use_DFS1__(
                    k_sub, v_sub, subNode["children"])

    def __vSet_convert__(self, vSet: dict):
        """
        将类似{0: "a", 1: "b"}的参数列表转化为["0 :: a", "1 :: b"]的格式
        """
        return ["{0:n} :: {1:s}".format(k, v) for (k, v) in vSet.items()]


class Maps_Editor_Main_Widget(QMainWindow):
    valueChanged = pyqtSignal()

    def __init__(self):
        super(Maps_Editor_Main_Widget, self).__init__()

        ###################################
        # 变量或对象
        self.dataIR = IR()
        self.dataBuffer = None  # 名义上还叫作“dataBuffer”，实质上已经是东周天子，象征性需要，跟main.py交互需要。数据大权在楼上。
        self.currentStage = ['1', '1']  # 当前正在操作的区段
        self.currentObj_id = -1  # 当前操作对象的id
        self.currentObj = None  # 当前正在操作的对象

        self.currentDir = pathlib.Path().home()  # TODO:要有跟main.py里一样的记忆功能
        self.IRFileDialog = QFileDialog(
            self, "打开专门记录地图的IR信息文件", str(self.currentDir), "*")

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
        self.objExplorer = Obj_Explorer()
        self.objExplorer.set_mapIR(
            self.dataIR.get_IR_data(), self.dataIR.get_IR_data_recycleBin())
        # print(self.dataIR.dataBuffer)
        self.objExplorer.objWasSelected.connect(self.change_current_obj)

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
        self.fileIO_ToolBar.btn_loadFullIR.clicked.connect(
            self.func_loadFullIR)

    #################################
    # 东周天子函数
    def get_data(self):
        return self.dataIR.get_json_dict()

    def set_data(self, LevelData: dict):
        self.dataIR.load_from_json_dict(LevelData)
        self.objExplorer.set_mapIR(self.dataIR.get_IR_data())
        # TODO:应该需要一个当即刷新的函数

    ###########################################
    # 按钮功能函数
    # TODO
    def func_loadFullIR(self):
        if (self.IRFileDialog.exec()):
            filePath = (self.IRFileDialog.selectedFiles())[0]  # 肯定只选择了1个文件
            self.dataIR.load_from_IR_file(filePath)
            self.dataIR.index_init()
            self.objExplorer.set_mapIR(
                self.dataIR.get_IR_data(), self.dataIR.get_IR_data_recycleBin())
            # self.objExplorer.tree_init()

    #################################
    def change_current_obj(self, _id: int):
        """
        改变当前关注的对象
        """
        print("当前关注对象id: {0:n}".format(_id))
        self.currentObj_id = _id
        self.currentObj = self.dataIR.objList[self.currentObj_id]


if (__name__ == "__main__"):
    app = QApplication([])
    window = Maps_Editor_Main_Widget()
    window.show()
    app.exec()
