import os
from pathlib import Path
from googletrans import Translator
import global_var
import re
import json
import snbtlib

MAGIC_WORD = r'{xdawned}'


class TextStyle:
    # 定義常量，表示不同顏色和特殊樣式
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    LIGHT_YELLOW = '\033[93m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    # 背景色
    BLACK_BG = '\033[40m'
    RED_BG = '\033[41m'
    GREEN_BG = '\033[42m'
    YELLOW_BG = '\033[43m'
    BLUE_BG = '\033[44m'
    MAGENTA_BG = '\033[45m'
    CYAN_BG = '\033[46m'
    WHITE_BG = '\033[47m'


def check_config_exists():
    filename = 'config.json'
    # 檢查文件是否存在
    if not os.path.exists(filename):
        # 創建一個空的配置字典
        config = {
            "QUESTS_PATH": "./ftbquests",
            "LANG_PATH": "./en_us.json",
            "KEEP_ORIGINAL": True,
            "BACK_FILL_PATH": "./ftbquests-trans",
            "BACK_FILL_LANG_PATH": "./zh_tw.json",
            "API": "LOCAL"
        }
        try:
            # 打開文件並寫入配置內容
            with open(filename, 'w') as file:
                json.dump(config, file, indent=1, ensure_ascii=False)
            print(f"配置文件已初始化於：{filename}")
        except Exception as e:
            print(f"未檢測到配置文件,在嘗試創建時出錯,你可以手動創建：{e}")
    else:
        print(f"[INFO]: {filename} Loaded")


def get_config():
    with open('config.json', 'r', encoding="utf-8") as fin:
        config_data = json.loads(fin.read())
        global_var.set_value('QUESTS_PATH', config_data['QUESTS_PATH'])
        global_var.set_value('LANG_PATH', config_data['LANG_PATH'])
        global_var.set_value('KEEP_ORIGINAL', config_data['KEEP_ORIGINAL'])
        global_var.set_value('BACK_FILL_PATH', config_data['BACK_FILL_PATH'])
        global_var.set_value('BACK_FILL_LANG_PATH', config_data['BACK_FILL_LANG_PATH'])
        global_var.set_value('API', config_data['API'])


def make_output_path(path: Path) -> Path:
    """
    生成輸出目錄，為原文件夾+trans
    :param path:輸入目錄路徑
    :return:自動生成的輸出目錄路徑
    """
    parts = list(path.parts)
    parts[0] = parts[0] + "-trans"
    output_path = Path(*parts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def check_low(text):
    match = re.search(r'\",$', text, re.MULTILINE)
    if match:
        print(TextStyle.BLUE, '檢測到1.12.2老版本任務文件!!!', TextStyle.RESET)
    return match


def get_snbt_quest(input_path: Path):
    with open(input_path, 'r', encoding="utf-8") as fin:
        quest = fin.read()
        low = check_low(quest)
        try:
            quest = snbtlib.loads(quest)  # 轉化為json格式並讀取
            return quest, low
        except TypeError:
            print(TextStyle.RED, 'snbtlib調用出錯，可能是python環境版本過低或其它問題！', TextStyle.RESET)


def translate_line(line: str) -> str:
    """
    翻譯送來的字符串
    :param line:字符串
    :return:翻譯結果字符串
    """
    API = global_var.get_value('API')
    if API == 'Google':

        # Send request
        translator = Translator()
        t = str(translator.translate(line, dest='zh-tw').text)
        return t

    else:
        print(TextStyle.RED, "翻譯模型調用出錯！", TextStyle.RESET)
        return line


# magic方法，這樣似乎就可以讓baidu不翻譯顏色代碼
def bracket(m: re.Match):
    return "[&" + m.group(0) + "]"


def debracket(m: re.Match):
    return m.group(0)[2:-1]


def back_fill_magic_word(line, translate, pattern, type_info=''):
    quotes = re.findall(pattern, line)  # 找出所有引用詞
    if len(quotes) > 0:
        print(TextStyle.YELLOW, f"在此行找到{type_info}", quotes, TextStyle.RESET)
        count = 0
        # 找出MAGIC_WORD出現的所有位置並替換為對應引用詞
        index = translate.find(MAGIC_WORD)
        while index != -1:
            translate = re.sub(MAGIC_WORD, quotes[count], translate, 1)
            count = count + 1
            index = translate.find(MAGIC_WORD)
    return translate


def add_escape_quotes(text, is_lang=False):
    # 匹配沒有添加單轉義符的引號，並為之添加
    pattern = r'(?<!\\)"'
    repl = r'\\"'
    result = re.sub(pattern, repl, text)
    if is_lang:
        result = result.replace('\\\"', '\"')
        result = result.replace('\\&', '&')
        result = result.replace('\\n', 'n')
        pattern = r'(?<!%)%'
        repl = r'%%'
        result = re.sub(pattern, repl, result)
    return result


def pre_process(line: str):
    API = global_var.get_value('API')
    # 情景1：圖片介紹
    if line.find('.jpg') + line.find('.png') != -2:
        print(TextStyle.YELLOW, '檢測到圖片', line, '已保留', TextStyle.RESET)
        return None  # 新版ftbquest可以展示圖片，遇到圖片則略過
    # 情景2：特殊事件，彩色或點擊action等
    if line.find(r'{\"') != -1:
        print(TextStyle.YELLOW, '檢測到特殊事件', line, '已保留', TextStyle.RESET)
        return None
    # 情景3：\\&表and
    line = line.replace('\\\\&', 'PPP')
    # 情景4：彩色區域
    # 彩色格式保留，讓百度api忽略&
    # 目前已知的彩色格式只有a~f,0~9全部依次錄入即可）百度api大多可以返回包含&.的漢化結果。
    pattern = re.compile(r'&([a-z,0-9]|#[0-9,A-F]{6})')
    # 將方括號替換回來
    if API == 'Baidu':
        line = pattern.sub(bracket, line)
    # 情景5：物品引用
    # 比如#minecraft:coals需要保留,打破此格式將會導致此章任務無法讀取！！！
    # 這裡給出的方案是先將引用替換為臨時詞MAGIC_WORD，術語庫中設置MAGIC_WORD-MAGIC_WORD來保留此關鍵詞，然後借此在翻譯後的句子中定位MAGIC_WORD用先前引用詞換回
    line = re.sub(r'#\w+:\w+\b', MAGIC_WORD, re.sub(r'\\"', '\"', line))  # 輔助忽略轉義符
    # 情景6：超鏈接
    pattern = re.compile(r'(http|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    if re.search(pattern, line):
        print(TextStyle.YELLOW, '檢測到超鏈接', line, '已保留', TextStyle.RESET)
        return None  # 某行包含超鏈接，保險策略，直接略過此行
    # 情景7：翻頁{@pagebreak}
    if re.search(r'\{@\w+}', line):
        print(TextStyle.YELLOW, '檢測到點擊事件', line, '已保留', TextStyle.RESET)
        return None  # 某行包含點擊事件，保險策略，直接略過此行
    return line


def post_process(line, translate):
    API = global_var.get_value('API')
    # 將方括號替換回來
    pattern = re.compile(r'\[&&([a-z,0-9]|#[0-9,A-F]{6})]')
    if API == 'Baidu':
        translate = pattern.sub(debracket, translate)
        line = pattern.sub(debracket, line)
    # 將物品引用換回
    translate = back_fill_magic_word(line=line, translate=translate, pattern=re.compile(r'#\w+:\w+\b'),
                                     type_info='物品引用')
    # translate = back_fill_magic_word(line=line, translate=translate, pattern=re.compile(r'\{@\w+}'), type_info='翻頁')
    # 修補缺失轉義符
    translate = add_escape_quotes(translate)
    return translate
