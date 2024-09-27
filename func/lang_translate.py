from func.base import *


def get_lang(input_path: Path) -> dict:
    with open(input_path, 'r', encoding="utf-8") as fin:
        quest = fin.read()
        try:
            quest = json.loads(quest)  # 轉化為json格式並讀取
            return quest
        except TypeError:
            print(TextStyle.RED, 'lang文件讀取出錯，可能是所讀取的json文件格式錯誤或其它問題！', TextStyle.RESET)


def update_lang_file(input_path: Path, output_path: Path):
    print('讀取成功，正在翻譯lang文件:', TextStyle.LIGHT_YELLOW, input_path, TextStyle.RESET)
    lang = get_lang(input_path)
    lang = update_lang(lang)  # 翻譯相應內容
    with open(output_path, 'w', encoding="utf-8") as fout:
        print(TextStyle.GREEN, '翻譯完成\n')
        fout.write(json.dumps(lang, indent=1, ensure_ascii=False))


def update_lang(lang: dict) -> dict:
    KEEP_ORIGINAL = global_var.get_value('KEEP_ORIGINAL')
    for key in lang:
        try:
            line = lang[key]
            pre_processed_line = pre_process(line)
            translate = translate_line(pre_processed_line) if pre_processed_line else line
            post_translate = post_process(line, translate)
            print(f"\r文本翻譯完成：\n原文：" + TextStyle.YELLOW + line + TextStyle.RESET)
            print("\r譯文：" + TextStyle.GREEN + post_translate + TextStyle.RESET)
            if KEEP_ORIGINAL:
                lang[key] = f"{line}[--{post_translate}--]"
            else:
                lang[key] = post_translate
        except Exception as e:
            print(TextStyle.RED + f'key：{key}項遇到錯誤{e}，請手動處理' + TextStyle.RESET)
            continue
    return lang


def make_output_path(path: Path) -> Path:
    parts = list(path.parts)
    parts[-1] = 'zh_tw.json'
    output_path = Path(*parts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def lang_trans():
    get_config()
    LANG_PATH = global_var.get_value('LANG_PATH')
    input_path = Path(LANG_PATH)  # 要翻譯的目錄
    output_path = make_output_path(input_path)  # 生成輸出目錄路徑
    update_lang_file(input_path, output_path)  # 更新任務文件
    print(TextStyle.CYAN, "你可以在en_us同級目錄下的trans文件夾中找到翻譯後的lang文件zh_tw.json.", TextStyle.RESET)
    print("************lang文件翻譯完成************")
