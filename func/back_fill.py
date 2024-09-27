from func.base import *


def get_lang(input_path: Path) -> dict:
    with open(input_path, 'r', encoding="utf-8") as fin:
        lang = fin.read()
        try:
            lang = json.loads(lang)  # 轉化為json格式並讀取
            return lang
        except TypeError:
            print(TextStyle.RED, 'lang文件讀取出錯，可能是所讀取的json文件格式錯誤或其它問題！', TextStyle.RESET)


def dict_replace(text, dic):
    for key, value in dic.items():
        text = text.replace('{' + key + '}', str(value))
    return text


def fill_back_file(lang: dict, input_path: Path, output_path: Path):
    print('讀取成功，正在回填lang文件:', TextStyle.LIGHT_YELLOW, input_path, TextStyle.RESET)

    with open(input_path, 'r', encoding="utf-8") as fin:
        quest = fin.read()
        with open(output_path, 'w', encoding="utf-8") as fout:
            fout.write(dict_replace(quest, lang))


def make_output_path(path: Path) -> Path:
    parts = list(path.parts)
    parts[0] = parts[0] + "-back"
    output_path = Path(*parts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def back_fill():
    get_config()
    BACK_FILL_PATH = global_var.get_value('BACK_FILL_PATH')
    BACK_FILL_LANG_PATH = global_var.get_value('BACK_FILL_LANG_PATH')
    file_path = Path(BACK_FILL_PATH)  # 要回填的任務目錄
    lang_path = Path(BACK_FILL_LANG_PATH)  # 要回填的lang文件地址
    lang = get_lang(lang_path)
    for input_path in file_path.rglob("*.snbt"):
        output_path = make_output_path(input_path)  # 生成輸出目錄路徑
        fill_back_file(lang, input_path, output_path)
    print(TextStyle.CYAN, "你可以在zh_tw.json的同級目錄下的-back文件夾中找到回填後的snbt文件.", TextStyle.RESET)
    print("================lang文件回填完成================")
