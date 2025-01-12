"""
在json数据与图形界面所示之间的一层中间表示与编译系统。
"""
import copy
import json
import sys
import ast
import pprint


def __template_read__():
    with open("map_things.json", "rt", encoding="utf-8") as jsonfile:
        return json.load(jsonfile)


TEMPLATE_JSON = __template_read__()


class Encoder():
    """
    从模板json文件读取对象，并转化为IR的格式
    """

    def __init__(self):
        ##########################
        # 读入数据模板
        self._templateJson = copy.deepcopy(
            TEMPLATE_JSON)  # __template_read__()
        # 表示类型的特定字符串与对应转换函数或类之间的对应关系
        self.__typeDict__ = {"int": int, "bool": self.__str2bool__, "str": str}
        self.__enemyNameDict__ = self.__enemyNameDict_read__()

        # 函数同名定义
        self.mergeDataFromJson = self.mergeEnemyDataFromJson

    def __enemyNameDict_read__(self):
        jsonfile = open("enemies.json", "rt", encoding="utf-8")
        data = json.load(jsonfile)
        jsonfile.close()

        return {item["name"]: item for item in data}

    def buildEmptyEnemyIR(self, objArgs) -> dict:
        # objName: str, objCommonName: str) -> dict:
        """
        构建空IR模板的函数。名字带“enemy”只是因为最早为敌人单位设计，现扩大可用范围，但是懒得改名了，由一个前端函数间接调用。
        objArgs: 一个有顺序的可迭代对象，一般是(对象具体名, 通用模板名, 系列名)，例如：("enemy01", "enemy_common" ,"enemies")
        """
        (objName, objCommonName, objSeriesName) = objArgs
        obj = copy.deepcopy(self._templateJson[objCommonName])
        # Warning: update方法也需要考虑是否使用深拷贝！若未拷贝，传的参仅为指针，修改一次即已变动。造成本函数“一次性”的BUG。
        obj.update(copy.deepcopy(self._templateJson[objSeriesName][objName]))
        # print(obj)
        # for (k_parent, v_parent) in obj:
        #    if (type(v_parent) == type(dict())):
        #        # for (k_sub,v_sub) in v_parent:
        #        #    if(type(v_sub)==type(dict())):
        #        if (type(v_parent["values"]) == type(dict())):
        #            obj[k_parent]["values"] = self.__dict_convert__(
        #                obj[k_parent]["values"])
        #
        # for (k_parent, v_parent) in self._templateJson["enemies"][enemyName]:
        #    match type(v_parent):
        #        case type(dict()):
        #            pass
        #        case type(list()):
        #            pass
        #        case _:
        #            obj[k_parent] = v_parent
        self.__buildEmptyEnemyIR_DFS1__(obj)
        # print("DFS1处理后的对象：\n{0}".format(obj))
        self.__buildEmptyEnemyIR_DFS2__(obj)
        # print("DFS2处理后的对象：\n{0}".format(obj))

        #######################################################
        # 杂项处理
        if (objSeriesName == "enemies"):  # 只有敌人对象才可能需要从已有列表补充单位名
            enemyName = objName
            if (obj["dest"] == None):
                enemy = self.__enemyNameDict__.get(enemyName, None)
                if (enemy):
                    obj["dest"] = enemy["dest"]

        obj["name"] = objName  # 加上主键，怎么最容易被忘记呢？

        return obj

    def __buildEmptyEnemyIR_DFS1__(self, obj):
        """
        利用DFS递归转换处理json文件中的数据。
        1. 处理值字典
        """
        # print(obj)
        if (type(obj) == type(dict())):
            # print(self.__is_selectable_values_dict__(obj))
            # if (self.__is_selectable_values_dict__(obj)):  # 如果是值字典，则处理
            #    obj = self.__dict_convert__(obj)
            #    print(obj)
            # else:  # 否则向下递归
            for (k, v) in obj.copy().items():
                if (type(v) == type(dict()) and self.__is_selectable_values_dict__(v)):  # 如果是值字典，则处理
                    obj[k] = self.__dict_convert1__(v)

                    # 给在只能值字典中选择(只能选不能自定)的参数，赋予None初值
                    obj["{0:s}_current".format(k)] = 0
                elif (v == -32768):
                    obj["{0:s}_current".format(k)] = 0
                else:  # 否则向下递归
                    self.__buildEmptyEnemyIR_DFS1__(v)
        elif (type(obj) == type(list())):  # 若遇到一般的可迭代对象等，json中的数组默认只会转换为list。json中只有数组，没有集合。
            for i in obj:
                self.__buildEmptyEnemyIR_DFS1__(i)

    def __buildEmptyEnemyIR_DFS2__(self, obj):
        """
        DFS处理数据
        2. 转换list型
        """
        if (type(obj) == type(dict())):
            for (k, v) in obj.copy().items():
                if ((type(v) == type(list())) and self.__is_vars_list__(v)):  # 如果是参数列表，则处理
                    obj[k] = self.__dict_convert2__(v)
                else:  # 否则向下递归
                    self.__buildEmptyEnemyIR_DFS2__(v)
        elif (type(obj) == type(list())):
            for i in obj:
                self.__buildEmptyEnemyIR_DFS2__(i)

    def __is_selectable_values_dict__(self, _dict: dict) -> bool:
        """
        判断是不是{值 -> 类型: 描述}格式的字典。称为“值字典”
        """
        # print(_dict)
        for k in _dict:
            if (not ("->" in k)):
                return False
        return True

    def __is_vars_list__(self, _list: list) -> bool:
        """
        检查是否是参数列表。
        一般形式是：
            vars: [{"key": xxx, "values": xxx, "dest": xxx}, ...]
        """
        for i in _list:
            if (type(i) == type(dict())):
                if (not ({"key", "value"}.issubset(set(i.keys())))):
                    return False
            else:
                return False
        return True

    def __dict_convert1__(self, jsonDict: dict) -> dict:
        """
        转化json中{值 -> 类型: 描述}格式的字典为python支持的字典。
        """
        newDict = dict()
        for (k, v) in jsonDict.items():
            (k_v, k_type) = k.split("->")
            (k_v, k_type) = (k_v.strip(), k_type.strip())
            k2 = self.__typeDict__[k_type](k_v)
            newDict[k2] = v

        return newDict

    def __dict_convert2__(self, varList: list) -> dict:
        """
        将现版本json文件的vars列表："vars": [{"A": ...}, {"B": ...}]
        转化为IR格式的："vars": {"varNameList": ["A", "B"], "A": {"A": ...}, "B": {"B": ...}}
        """
        varNameList = [var["key"] for var in varList]
        newVars = dict()
        newVars["varNameList"] = varNameList
        for i in varList:
            newVars[i["key"]] = i

        return newVars

    def __str2bool__(s: str) -> bool:
        match s.lower():
            case "true":
                return True
            case "false":
                return False
            case _:
                print("“{0:s}”不是表示“True”或“False”的单词！".format(s))
                sys.exit(1)

    def mergeEnemyDataFromJson(self, enemyObjKV):
        """
        KV指(k, v)键值对，它们不一定是tuple，故未作限定
        """
        (enemyObjK, enemyObjV) = enemyObjKV
        (enemyName, x, y) = enemyObjK.split(">")
        # x = ast.literal_eval(x)
        # y = ast.literal_eval(y)
        x = self.__str2mathNum__(x)
        y = self.__str2mathNum__(y)

        # enemyIRObj = self.buildEmptyEnemyIR(enemyName=enemyName)
        enemyIRObj = self.buildEmptyIR(objName=enemyName)
        enemyIRObj["pos"] = [x, y]

        self.__mergeEnemyDataFromJson_DFS__(enemyObjV, enemyIRObj)

        return enemyIRObj

    def __mergeEnemyDataFromJson_DFS__(self, obj_js, obj_ir):
        if (type(obj_js) == type(dict())):
            for k in obj_js.copy():
                self.__mergeEnemyDataFromJson_DFS__(obj_js[k], obj_ir[k])
        elif (type(obj_js) == type(list())):
            for i in obj_js:
                targetIRObj = obj_ir[i["key"]]
                currentKey = self.__find_key_current__(targetIRObj)
                if (currentKey):
                    targetIRObj[currentKey] = i["value"]
                # self.__mergeEnemyDataFromJson_DFS__(i, obj_ir[i["key"]])
        else:
            obj_ir["values_current"] = obj_js

    # def convertEnemyModJsonDict2IR(self, _dict: dict):
    #    _dict = copy.deepcopy(_dict)
    #
    # def __convertEnemyModJsonDict2IR_DFS__(self, obj):
    #    if (type(obj) == type(list())):
    #        for i in obj:
    #            self.__convertEnemyModJsonDict2IR_DFS__(i)
    #    elif (type(obj) == type(dict())):
    #        for (k, v) in obj.copy().items():
    #            pass

    def __find_key_current__(self, _dict: dict) -> str:
        for key in _dict:
            if (key.endswith("_current")):
                return key

    def __str2mathNum__(self, s: str):
        (i, f) = (int(s), float(s))
        if (i == f):
            return i
        else:
            return f

    def __mod_json_read__(self):
        with open(filename, "rt", encoding="utf-8") as jsonfile:
            return json.load(jsonfile).get("LevelData")

    def buildEmptyIR(self, objName: str) -> dict:
        # for keyWord in ("enemy","object","other","lock"):
        if (objName.startswith("enemy")):
            return self.buildEmptyEnemyIR([objName, "enemy_common", "enemies"])
        elif (objName.startswith("object")):
            return self.buildEmptyEnemyIR([objName, "object_common", "objects"])
        elif (objName.startswith("other")):
            return self.buildEmptyEnemyIR([objName, "other_common", "others"])
        elif (objName.startswith("lock")):
            return self.buildEmptyEnemyIR([objName, "lock_common", "locks"])

    # def mergeDataFromJson(self,objName:str):


class IR():
    """
    IR化数据的处理中心
    """

    def __init__(self):
        ###################################
        # 几个变量
        self.dataBuffer = self.__dataBuffer_init__()
        self.ed = Encoder()
        self.pp4IR = pprint.PrettyPrinter(sort_dicts=False)

    def __dataBuffer_init__(self):
        """
        IR数据结构：
        {
            Level号: {
                "场景1": {
                    "objects": [
                        {"name": "enemy01", ...},
                        {"name": "object01", ...},
                        ...
                    ],
                    "locks": [
                        {"name": "lock", ...},
                        {"name": "lock", ...},
                    ]
                },
                "场景2": {...},
                ...
            }
        }
        """
        emptyLevel = dict()
        levels_template = TEMPLATE_JSON["levels"]

        ############################################
        # level-mission 对应关系
        diff_mission = dict()
        level_nums = []
        for (mission, levels2) in levels_template["mission-diff"].items():
            level_nums += levels2
            for level in levels2:
                diff_mission[level] = mission

        level_nums.sort()
        for level in level_nums:
            emptyLevel[str(level)] = dict()
            levelDict = emptyLevel[str(level)]
            for s in levels_template["topographies"][diff_mission[level]]:
                levelDict[s] = {"objects": [], "locks": []}

        return emptyLevel

    def load_from_jsonDict(self, dict_js: dict):
        """
        从mod的json文件转换所得dict中读取关卡数据
        即_dict["LevelData"]
        """
        for (stageName, stage) in dict_js.items():
            (level, stageNum) = self.__key_split__(stageName)
            for kv in stage.items():
                obj_ir = self.ed.mergeDataFromJson(kv)
                if (obj_ir["name"] == "lock"):
                    self.dataBuffer[level][stageNum]["locks"].append(obj_ir)
                else:
                    self.dataBuffer[level][stageNum]["objects"].append(obj_ir)

        print("已成功读入\n{0}".format(self.dataBuffer))

    def __key_split__(self, key: str):
        """
        处理类似"sx_y"的键名，读取为[x: str, y: str]
        """
        key = key.lstrip('s')
        # key = tuple(int(i) for i in key.split('_'))
        key = key.split('_')

        return key

    def get_IR_str(self) -> str:
        """
        获取IR表示，利用pprint美化，便于查看
        IR表示的备份与还原仅仅是附带功能。
        """
        return self.pp4IR.pformat(self.dataBuffer)

    def load_from_IR_str(self, str_ir: str):
        """
        读取IR表示的字符串，转化为IR数据
        """
        if (self.pp4IR.isreadable(str_ir)):
            self.dataBuffer = ast.literal_eval(str_ir)
            print("已成功读入\n{0}".format(self.dataBuffer))
        else:
            print("此字符串无法被解析为可读取的数据")
            sys.exit(1)


class JsonDictCompiler():
    """
    从IR编译生成适用于mod json文件的数据
    """

    def __init__(self):
        pass

    def buildEnemyDict4Json(self, enemyIRObj: dict, n: int = 0) -> dict:
        """
        由中间表示(IR)，向适配游戏的json对象转换。
        enemyIRObj：IR格式的敌人对象
        n：用于处理重叠的单位，默认0则生成整数，否则取小数点后n位。如n=0时，enemy01>114>514；n=1时,enemy01>114>514.0
        因为是IR，是固定格式，所以敢写死。
        """

        if (n):
            keyNameFmt = "{0:s}>{1:.%uf}>{2:n}" % (n)
        else:
            keyNameFmt = "{0:s}>{1:n}>{2:n}"
        (x, y) = enemyIRObj["pos"]
        keyName = keyNameFmt.format(enemyIRObj["name"], x, y)

        jsonObj = copy.deepcopy(enemyIRObj)
        self.__buildEnemyDict4Json_DFS__(jsonObj)

        return {keyName: jsonObj}

    def __is_value_dict__(self, _dict: dict) -> int:
        """
        struct typeCode
        {
            unsigned int isValueDict: 1;
            unsigned int isValueDictList: 1;
        };
        """
        typeCode = 0
        for k in _dict:
            if (type(k) == type(str())):
                if (k == "varNameList"):
                    typeCode |= 0b01
                elif (k.endswith("_current")):
                    typeCode |= 0b10

        return typeCode

    def __buildEnemyDict4Json_DFS__(self, obj):
        if (type(obj) == type(dict())):
            for (k, v) in obj.items():
                if (type(v) == type(dict())):
                    # obj.setdefault(k,dict())
                    typeCode_v = self.__is_value_dict__(v)
                    if (typeCode_v & 0b10):
                        valueKeyName = self.__find_key_current__(v)
                        obj[k] = v[valueKeyName]
                    elif (typeCode_v & 0b01):
                        obj[k] = [v[varName] for varName in v["varNameList"]]
                        self.__buildEnemyDict4Json_DFS__(obj[k])
                    else:
                        self.__buildEnemyDict4Json_DFS__(v)
        elif (type(obj) == type(list())):
            for i in obj:
                self.__buildEnemyDict4Json_DFS__(i)

    def __find_key_current__(self, _dict: dict) -> str:
        for k in _dict:
            if (k.endswith("_current")):
                return k

    def __dict_convert2__(self, varDict: dict):
        """
        1用于纯字典，2用于列表参数的。约定俗成吧。
        """
        return [varDict[varName] for varName in varDict["varNameList"]]


if (__name__ == "__main__"):
    i = Encoder()
    # enemy = "enemy01_2"
    # enemies = ["enemy%02d" % (i) for i in range(1, 43+1)]
    # enemies.remove("enemy24")
    # for enemy in enemies:
    #    print("\n\n{0:s}对象的中间表示空模板为：\n{1}".format(
    #        enemy, i.buildEmptyEnemyIR(enemy)))
    print(i.buildEmptyIR("enemy01"), "\n\n")
    print(i.buildEmptyIR("object01"), "\n\n")
    print(i.buildEmptyIR("other01"), "\n\n")
    print(i.buildEmptyIR("lock"), "\n\n")

    # print(i.buildEmptyEnemyIR("enemy12"), "\n\n")
    enemyData = ("enemy12>102>98", {"ammo": 1, "boss": 1, "vars": [{"key": "atks", "value": 1}, {
        "key": "movNsta", "value": 0}], "xMax": {"value": 6}, "xMin": {"value": 1}, "xscale": 100})
    lockData = ("lock>124>43", {"wave": 3, "xscale": 100})
    objectData = ("object04>504>76", {"ammo": 1, "xscale": 100})
    otherData = ("other01>288>295", {"xscale": -100})

    # ir = i.mergeEnemyDataFromJson(enemyData)
    # cc = JsonDictCompiler()
    # out = cc.buildEnemyDict4Json(ir)
    # print("源json格式数据：\n{0}\n\n转换为中间格式：\n{1}\n\n编译回游戏用json格式：\n{2}".format(
    #    enemyData, ir, out))

    ir = IR()
    # pp=pprint.PrettyPrinter(sort_dicts=False)
    # pp.pprint(ir.dataBuffer)

    map_test3_file = open("scw.json", "rt")
    map_test3_data = json.load(map_test3_file)
    map_test3_file.close()

    ir.load_from_jsonDict(map_test3_data["LevelData"])
    map_test3_data_IR = ir.get_IR_str()
    ir.load_from_IR_str(map_test3_data_IR)

    with open("/tmp/scw.mapIR.txt", "wt") as mapfile:
        mapfile.write(map_test3_data_IR)
