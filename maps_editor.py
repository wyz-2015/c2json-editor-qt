import copy
import json
import sys


class IR():
    """
    在json数据与图形界面所示之间的一层中间表示与编译系统。
    """

    def __init__(self):
        ##########################
        # 读入数据模板
        self._templateJson = self.__template_read__()
        self.__typeDict__ = {"int": int, "bool": __str2bool__}  # 表示类型的特定字符串与对应转换函数或类之间的对应关系
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
        print("DFS1处理后的对象：\n{0}".format(obj))
        self.__buildEmptyEnemyIR_DFS2__(obj)
        print("DFS2处理后的对象：\n{0}".format(obj))

        # 3
        # 杂项处理
        if (obj["dest"] == None):
            enemy = self.__enemyNameDict__.get(enemyName, None)
            if (enemy):
                obj["dest"] = enemy["dest"]

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
                    obj["{0:s}_current".format(k)] = None
                elif(v==-32768):
                    obj["{0:s}_current".format(k)] = None
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
        varNameList = [var["key"] for var in varList]
        newVars = dict()
        newVars["varNameList"] = varNameList
        for i in varList:
            newVars[i["key"]] = i

        return newVars

def __str2bool__(s: str):
    match s.lower():
        case "true":
            return True
        case "false":
            return False
        case _:
            print("“{0:s}”不是表示“True”或“False”的单词！".format(s))
            sys.exit(1)


if (__name__ == "__main__"):
    i = IR()
    enemy = "enemy01_2"
    print("\n\n{0:s}对象的中间表示空模板为：\n{1}".format(
        enemy, i.buildEmptyEnemyIR(enemy)))
