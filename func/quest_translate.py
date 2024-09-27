import logging
from copy import copy

from nbt import nbt
from tqdm import tqdm
from func.base import *

LOW = False


def trans_field_snbt(quest: dict) -> dict:
    """
    翻譯此層關鍵字段（不涉及內部）
    :param quest:任務dict
    :return:完成指定的部分翻譯的dict
    """
    trans_key = ['title', 'subtitle', 'text', 'description']
    KEEP_ORIGINAL = global_var.get_value('KEEP_ORIGINAL')
    for key in quest:
        try:
            if key in trans_key:  # 匹配到關鍵key才進行翻譯
                if isinstance(quest[key], list):  # 文本可能多行，以list形式為判斷
                    line_list = quest[key]
                    post_translate_list = []
                    for index in range(0, len(line_list)):
                        line_text = line_list[index]
                        # 排除不包含字母的無意義文本(需確保字母不是由彩色格式引起)
                        content_validator = bool(re.search('[a-zA-Z]', re.sub(r'&[a-zA-Z0-9]', '', line_text)))
                        if bool(content_validator):  # 翻譯時忽略無字母的無效行
                            print("===========================================")
                            print(f"\rINPUT:\n{TextStyle.YELLOW + line_text + TextStyle.RESET}")
                            pre_line = pre_process(line_text)
                            if pre_line:  # 空返回為圖片，保留，不處理
                                translate = translate_line(pre_line)
                                post_translate = post_process(pre_line, translate)
                                post_translate_list.append(post_translate)
                            else:
                                post_translate_list.append(line_text)
                            print(f"RETURN:{TextStyle.GREEN + post_translate_list[-1] + TextStyle.RESET}")
                            print("===========================================")
                        else:
                            post_translate_list.append(line_text)
                    if KEEP_ORIGINAL:
                        quest[key] = post_translate_list + quest[key]
                    else:
                        quest[key] = post_translate_list
                else:  # 單行文本
                    text = pre_process(quest[key])
                    if text:
                        translate = translate_line(text)
                        post_translate = post_process(quest[key], translate)
                        print("===========================================")
                        print(f"\rINPUT:\n{TextStyle.YELLOW+text}\nRETURN:{TextStyle.GREEN+post_translate+TextStyle.RESET}")
                        print("===========================================")
                        if KEEP_ORIGINAL:
                            quest[key] = f"{post_translate}[--{quest[key]}--]"
                        else:
                            quest[key] = post_translate
        except Exception as e:
            logging.exception(e)
            print(TextStyle.RED + f'值為{quest[key]}的項遇到錯誤{e}，請手動處理' + TextStyle.RESET)
            continue
    return quest


def update_snbt(quest: dict) -> dict:
    """
    更新任務中需要漢化的區域
    :param quest:任務dict
    :return:漢化後任務dict
    """
    quest = trans_field_snbt(quest)  # 章節內容翻譯
    quest_child = ['quests', 'chapter_groups']  # 選擇翻譯的內層節點（quests為章節下任務,chapter_groups為目錄）
    for child in quest_child:
        if quest.get(child):
            quests = quest[child]
            for index in range(0, len(quests)):
                quests[index] = trans_field_snbt(quests[index])
            quest.update({child: quests})  # 覆蓋
    if quest.get('quests'):
        quests_child = ['tasks']  # 任務中子節點quests下還可能存在更細一層的子任務tasks
        for child in quests_child:
            for i in range(0, len(quest['quests'])):  # quests可能有多個
                if quest['quests'][i].get(child):
                    tasks = quest['quests'][i][child]
                    for index in range(0, len(tasks)):  # tasks可能有多個
                        tasks[index] = trans_field_snbt(tasks[index])
                    quest['quests'][i].update({child: tasks})  # 覆蓋原先quests下tasks
    return quest


def update_snbt_file(input_path: Path, output_path: Path) -> None:
    """
    更新文件，將處理完的文本寫回
    :param input_path:輸入目錄
    :param output_path:輸出目錄
    :return:無
    """
    global LOW
    print("正在處理:" + TextStyle.LIGHT_YELLOW + str(input_path) + TextStyle.RESET)
    quest, LOW = get_snbt_quest(input_path)
    quest = update_snbt(quest)  # 翻譯相應內容
    with open(output_path, 'w', encoding="utf-8") as fout:
        fout.write(snbtlib.dumps(quest, compact=LOW))


def update_nbt(quest: nbt.NBTFile) -> nbt.NBTFile:
    quest = trans_field_snbt(quest)  # 章節內容翻譯
    quest_child = ['quests', 'chapter_groups']  # 選擇翻譯的內層節點（quests為章節下任務,chapter_groups為目錄）
    for child in quest_child:
        if quest.get(child):
            quests = quest[child]
            for index in range(0, len(quests)):
                quests[index] = trans_field_snbt(quests[index])
            quest.update({child: quests})  # 覆蓋
    if quest.get('quests'):
        quests_child = ['tasks']  # 任務中子節點quests下還可能存在更細一層的子任務tasks
        for child in quests_child:
            for i in range(0, len(quest['quests'])):  # quests可能有多個
                if quest['quests'][i].get(child):
                    tasks = quest['quests'][i][child]
                    for index in range(0, len(tasks)):  # tasks可能有多個
                        tasks[index] = trans_field_snbt(tasks[index])
                    quest['quests'][i].update({child: tasks})  # 覆蓋原先quests下tasks
    return quest


def trans_field_nbt(quest):
    quest = copy(quest)
    trans_key = ['title', 'description', 'text']
    KEEP_ORIGINAL = global_var.get_value('KEEP_ORIGINAL')
    for key in quest.keys():
        try:
            if key in trans_key:  # 匹配到關鍵key才進行翻譯
                if type(quest[key]) == nbt.TAG_List:  # 文本可能多行，以list形式為判斷
                    line_list = quest[key]
                    post_translate_list = []
                    for index in range(0, len(line_list)):
                        if bool(re.search('[a-zA-Z]', line_list[index].value)):  # 忽略無字母的無效行
                            pre_line = pre_process(line_list[index].value)
                            if pre_line:  # 空返回為圖片，保留，不處理
                                translate = translate_line(pre_line)
                                post_translate = post_process(pre_line, translate)
                                post_translate_list.append(post_translate)
                                print(f"\r翻譯中：\n{TextStyle.YELLOW+pre_line}\n{TextStyle.GREEN+post_translate+TextStyle.RESET}")
                    if KEEP_ORIGINAL:
                        quest[key].value = post_translate_list + quest[key].value
                    else:
                        quest[key].value = post_translate_list
                else:  # 單行文本
                    line = quest[key].value
                    pre_line = pre_process(line)
                    if pre_line:
                        translate = translate_line(pre_line)
                        post_translate = post_process(quest[key].value, translate)
                        print(f"\r翻譯中：\n{TextStyle.YELLOW+line}\n{TextStyle.GREEN+post_translate+TextStyle.RESET}")
                        if KEEP_ORIGINAL:
                            quest[key].value = f"{line}[--{post_translate}--]"
                        else:
                            quest[key].value = post_translate
        except Exception as e:
            print(TextStyle.RED + f'值為{quest[key]}的項遇到錯誤{e}，請手動處理' + TextStyle.RESET)
            continue
    return quest


def update_nbt_file(input_path: Path, output_path: Path) -> None:
    print("正在處理:" + TextStyle.LIGHT_YELLOW + str(input_path) + TextStyle.RESET)
    quest = get_nbt_quest(input_path)
    if quest.get('tasks'):
        for i in range(0, len(quest['tasks'])):
            quest['tasks'][i] = trans_field_nbt(quest['tasks'][i])
    quest = trans_field_nbt(quest)
    quest.write_file(output_path)


def get_nbt_quest(input_path: Path) -> nbt.NBTFile:
    try:
        nbtfile = nbt.NBTFile(input_path, 'rb')
        return nbtfile
    except Exception:
        print(TextStyle.RED, 'nbt讀取出錯！', TextStyle.RESET)


def quest_trans():
    get_config()
    QUESTS_PATH = global_var.get_value('QUESTS_PATH')
    quest_path = Path(QUESTS_PATH)  # 要翻譯的目錄
    t = list(quest_path.rglob("*.snbt"))
    for i in tqdm(range(0, len(t)), colour='#0396FF'):
        try:
            input_path = t[i]
            output_path = make_output_path(input_path)  # 生成輸出目錄路徑
            update_snbt_file(input_path, output_path)  # 更新任務文件
        except Exception as ex:
            print(TextStyle.RED, f"{i}在翻譯時遇到錯誤:{ex}", TextStyle.RESET)
            continue
    t = list(quest_path.rglob("*.nbt"))
    for i in tqdm(range(0, len(t)), colour='#0396FF'):
        try:
            input_path = t[i]
            output_path = make_output_path(input_path)  # 生成輸出目錄路徑
            update_nbt_file(input_path, output_path)  # 更新任務文件
        except Exception as ex:
            print(TextStyle.RED, f"{i}在翻譯時遇到錯誤:{ex}", TextStyle.RESET)
            continue

    print("================翻譯任務完成================")
