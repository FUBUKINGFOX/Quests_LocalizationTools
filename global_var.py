global _global_dict
_global_dict = {}


def set_value(key, value):
    # 定義一個全局變量
    _global_dict[key] = value


def get_value(key):
    # 獲得一個全局變量，不存在則提示讀取對應變量失敗
    try:
        return _global_dict[key]
    except:
        print('讀取' + key + '失敗\r\n')
