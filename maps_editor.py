"""
在json数据与图形界面所示之间的一层中间表示与编译系统。
"""
import copy
import json
import sys
# import ast


class Encoder():
    """
    从模板json文件读取，并转化为IR的模板
    """

    def __init__(self):
        ##########################
        # 读入数据模板
        self._templateJson = self.__template_read__()
        # 表示类型的特定字符串与对应转换函数或类之间的对应关系
        self.__typeDict__ = {"int": int, "bool": self.__str2bool__, "str": str}
        self.__enemyNameDict__ = self.__enemyNameDict_read__()

    def __template_read__(self):
        with open("map_things.json", "rt", encoding="utf-8") as jsonfile:
            return json.load(jsonfile)

    def __enemyNameDict_read__(self):
        jsonfile = open("enemies.json", "rt", encoding="utf-8")
        data = json.load(jsonfile)
        jsonfile.close()

        return {item["name"]: item for item in data}

    def buildEmptyEnemyIR(self, enemyName: str) -> dict:
        obj = copy.deepcopy(self._templateJson["enemy_common"])
        obj.update(self._templateJson["enemies"][enemyName])
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

        # 33
        # 杂项处理
        if (obj["dest"] == None):
            enemy = self.__enemyNameDict__.get(enemyName, None)
            if (enemy):
                obj["dest"] = enemy["dest"]

        obj["name"] = enemyName  # 加上主键，怎么最容易被忘记呢？

        return obj

    def __buildEmptyEnemyIR_DFS1__(self, obj):
        """
        利用DFS递归转换处理json文件中的数据。
        1. 处理值字典
        """
        # print(type(obj))
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
            for (k, v) in obj.items():
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
                if (not ({"key", "values"}.issubset(set(i.keys())))):
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

        enemyIRObj = self.buildEmptyEnemyIR(enemyName=enemyName)
        enemyIRObj["pos"] = [x, y]

        self.__mergeEnemyDataFromJson_DFS__(enemyObjV, enemyIRObj)

        return enemyIRObj

    def __mergeEnemyDataFromJson_DFS__(self, obj_js, obj_ir):
        if (type(obj_js) == type(dict())):
            for k in obj_js.copy():
                self.__mergeEnemyDataFromJson_DFS__(obj_js[k], obj_ir[k])
        elif (type(obj_js) == type(list())):
            for i in obj_js:
                obj_ir[i["key"]]["values_current"] = i["value"]
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

    def __str2mathNum__(self, s: str):
        (i, f) = (int(s), float(s))
        if (i == f):
            return i
        else:
            return f

    def __mod_json_read__(self):
        with open(filename, "rt", encoding="utf-8") as jsonfile:
            return json.load(jsonfile).get("LevelData")


class IR():
    """
    IR化数据的处理中心
    """

    def __init__(self):
        self.dataBuffer = dict()


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
        jsonObj = dict()

        if (n):
            keyNameFmt = "{0:s}>{1:.%uf}>{2:n}" % (n)
        else:
            keyNameFmt = "{0:s}>{1:n}>{2:n}"
        (x, y) = enemyIRObj["pos"]
        keyName = keyNameFmt.format(enemyIRObj["name"], x, y)


if (__name__ == "__main__"):
    i = Encoder()
    # enemy = "enemy01_2"
    # enemies = ["enemy%02d" % (i) for i in range(1, 43+1)]
    # enemies.remove("enemy24")
    # for enemy in enemies:
    #    print("\n\n{0:s}对象的中间表示空模板为：\n{1}".format(
    #        enemy, i.buildEmptyEnemyIR(enemy)))

    enemyData = ("enemy12>102>98", {"ammo": 1, "boss": 1, "vars": [{"key": "atks", "value": 1}, {
                 "key": "movNsta", "value": 0}], "xMax": {"value": 6}, "xMin": {"value": 1}, "xscale": 100})
    print(i.mergeEnemyDataFromJson(enemyData))
