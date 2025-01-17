from tqdm import tqdm
from nbt import nbt
from func.base import *
from global_var import *
from pathlib import Path
import re
import snbtlib
import json
from func.quest_translate import get_nbt_quest, get_snbt_quest

LOW = False


def get_snbt_value(prefix: str, text):
    """
    為key賦予value（多行與圖片)
    :param text:文本
    :param prefix:鍵名前綴
    :return 處理為鍵值後的原文
    """
    key_value = {}  # 用於存放新生成的鍵值及其對應的文本
    if isinstance(text, list):
        for i in range(0, len(text)):
            if bool(re.search(r'\S', text[i])):  # 非空行，為此行生成鍵值
                if text[i].find('{image:') == -1:  # 非圖片
                    if text[i] not in ['{@pagebreak}']:  # 非翻頁
                        local_key = (prefix + str(i)) if len(text) > 1 else prefix
                        key_value[local_key] = add_escape_quotes(text[i], True)
                        # 調整snbtlib讀取到的部分添加雙轉義符的文本
                        text[i] = '{' + local_key + '}'
        # list為可變類型，可省去一步處理
        return key_value, None
    else:
        if text.find('{image:') == -1:  # 非圖片
            key_value[prefix] = add_escape_quotes(text, True)
            text = '{' + prefix + '}'

        return key_value, text


def get_nbt_value(prefix: str, text):
    key_value = {}  # 用於存放新生成的鍵值及其對應的文本
    if type(text) == nbt.TAG_List:
        for i in range(0, len(text)):
            if bool(re.search(r'\S', text[i].value)):  # 非空行，為此行生成鍵值
                if text[i].value.find('{image:') == -1:  # 非圖片
                    local_key = (prefix + str(i)) if len(text) > 1 else prefix
                    key_value[local_key] = text[i].value
                    text[i].value = '{' + local_key + '}'
    else:
        if text.value.find('{image:') == -1:  # 非圖片
            key_value[prefix] = text.value
            text.value = '{' + prefix + '}'
    return key_value


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


def trans2lang():
    global LOW
    get_config()
    QUESTS_PATH = global_var.get_value('QUESTS_PATH')
    quest_path = Path(QUESTS_PATH)  # 要翻譯的目錄
    key_value = {}  # 用於存放新生成的鍵值及其對應的文本
    t = list(quest_path.rglob("*.snbt"))
    for i in tqdm(range(0, len(t)), colour='#0396FF'):
        try:
            input_path = t[i]
            output_path = make_output_path(input_path)
            quest, LOW = get_snbt_quest(input_path)
            prefix = '' + list(input_path.parts)[-1].replace('.snbt', '')  # 以snbt文件名為key的前綴便於回溯
            # chapter_groups-[title]
            if quest.get('chapter_groups'):
                chapter_groups = quest['chapter_groups']
                for i in range(0, len(chapter_groups)):
                    local_key = 'ftbquests.chapter_groups.' + prefix + '.title' + str(i)
                    new_key_value, new_text = get_snbt_value(local_key, chapter_groups[i]['title'])
                    if new_text:
                        chapter_groups[i]['title'] = new_text
                    key_value.update(new_key_value)
                # 寫入更新後的quest
                with open(output_path, 'w', encoding="utf-8") as fout:
                    print(TextStyle.GREEN, "************", output_path, "snbt替換結束************", TextStyle.RESET)
                    fout.write(snbtlib.dumps(quest, compact=LOW))
                continue

            # loot_tables-[title]
            if quest.get('loot_size'):  # 僅以鍵值判斷是否是loot_table內容
                if quest.get('title'):
                    local_key = 'ftbquests.reward_tables.' + prefix + '.title'
                    new_key_value, new_text = get_snbt_value(local_key, quest['title'])
                    if new_text:
                        quest['title'] = new_text
                    key_value.update(new_key_value)
                    # 寫入更新後的quest
                    with open(output_path, 'w', encoding="utf-8") as fout:
                        print(TextStyle.GREEN, "================", output_path, "snbt替換結束================", TextStyle.RESET)
                        fout.write(snbtlib.dumps(quest, compact=LOW))
                continue

            # data-[title]
            if quest.get('disable_gui'):  # 僅以鍵值判斷是否是loot_table內容
                if quest.get('title'):
                    local_key = 'ftbquests.data.' + prefix + '.title'
                    new_key_value, new_text = get_snbt_value(local_key, quest['title'])
                    if new_text:
                        quest['title'] = new_text
                    key_value.update(new_key_value)
                continue
            # chapter-[title,subtitle,text,description]
            if quest.get('title'):
                local_key = 'ftbquests.chapter.' + prefix + '.title'
                new_key_value, new_text = get_snbt_value(local_key, quest['title'])
                if new_text:
                    quest['title'] = new_text
                key_value.update(new_key_value)
            if quest.get('subtitle'):
                subtitle = quest['subtitle']
                if len(subtitle) > 0:
                    local_key = 'ftbquests.chapter.' + prefix + '.subtitle'
                    new_key_value, new_text = get_snbt_value(local_key, quest['subtitle'])
                    if new_text:
                        quest['subtitle'] = new_text
                    key_value.update(new_key_value)
            if quest.get('text'):
                text = quest['text']
                if len(text) > 0:
                    local_key = 'ftbquests.chapter.' + prefix + '.text'
                    new_key_value, new_text = get_snbt_value(local_key, quest['text'])
                    if new_text:
                        quest['text'] = new_text
                    key_value.update(new_key_value)
            if quest.get('description'):
                text = quest['description']
                if len(text) > 0:
                    local_key = 'ftbquests.chapter.' + prefix + '.description'
                    new_key_value, new_text = get_snbt_value(local_key, quest['description'])
                    if new_text:
                        quest['description'] = new_text
                    key_value.update(new_key_value)

            # chapter.images[i][hover]
            if quest.get('images'):
                images = quest['images']
                for i in range(0, len(images)):
                    if images[i].get('hover'):
                        hover = images[i]['hover']
                        if len(hover) > 0:
                            local_key = 'ftbquests.chapter.' + prefix + '.images' + str(i) + '.hover'
                            new_key_value, new_text = get_snbt_value(local_key, hover)
                            if new_text:
                                images[i]['hover'] = new_text
                            key_value.update(new_key_value)

            # chapter.quests[i][title,subtitle,description，text]
            # chapter.quests[i].tasks[j].[title,description]
            # chapter.quests[i].rewards[j].title
            if quest.get('quests'):
                quests = quest['quests']
                for i in range(0, len(quests)):
                    # title
                    if quests[i].get('title'):
                        title = quests[i]['title']
                        if len(title) > 0:
                            local_key = 'ftbquests.chapter.' + prefix + '.quests' + str(i) + '.title'
                            new_key_value, new_text = get_snbt_value(local_key, title)
                            if new_text:
                                quests[i]['title'] = new_text
                            key_value.update(new_key_value)
                    # subtitle
                    if quests[i].get('subtitle'):
                        subtitle = quests[i]['subtitle']
                        if len(subtitle) > 0:
                            local_key = 'ftbquests.chapter.' + prefix + '.quests' + str(i) + '.subtitle'
                            new_key_value, new_text = get_snbt_value(local_key, subtitle)
                            if new_text:
                                quests[i]['subtitle'] = new_text
                            key_value.update(new_key_value)
                    # description
                    if quests[i].get('description'):
                        description = quests[i]['description']
                        if len(description) > 0:
                            local_key = 'ftbquests.chapter.' + prefix + '.quests' + str(i) + '.description'
                            new_key_value, new_text = get_snbt_value(local_key, description)
                            if new_text:
                                quests[i]['description'] = new_text
                            key_value.update(new_key_value)
                    # text
                    if quests[i].get('text'):
                        text = quests[i]['text']
                        if len(text) > 0:
                            local_key = 'ftbquests.chapter.' + prefix + '.quests' + str(i) + '.text'
                            new_key_value, new_text = get_snbt_value(local_key, text)
                            if new_text:
                                quests[i]['text'] = new_text
                            key_value.update(new_key_value)
                    # tasks[j].title
                    if quests[i].get('tasks'):
                        tasks = quests[i]['tasks']
                        if len(tasks) > 0:
                            for j in range(0, len(tasks)):
                                if tasks[j].get('title'):
                                    title = tasks[j]['title']
                                    local_key = 'ftbquests.chapter.' + prefix + '.quests' + str(i) + '.tasks' + str(
                                        j) + '.title'
                                    new_key_value, new_text = get_snbt_value(local_key, title)
                                    if new_text:
                                        tasks[j]['title'] = new_text
                                    key_value.update(new_key_value)

                    # tasks[j].description
                    if quests[i].get('tasks'):
                        tasks = quests[i]['tasks']
                        if len(tasks) > 0:
                            for j in range(0, len(tasks)):
                                if tasks[j].get('description'):
                                    description = tasks[j]['description']
                                    local_key = 'ftbquests.chapter.' + prefix + '.quests' + str(i) + '.tasks' + str(
                                        j) + '.description'
                                    new_key_value, new_text = get_snbt_value(local_key, description)
                                    if new_text:
                                        tasks[j]['description'] = new_text
                                    key_value.update(new_key_value)

                    # rewards[j].title
                    if quests[i].get('rewards'):
                        rewards = quests[i]['rewards']
                        if len(rewards) > 0:
                            for j in range(0, len(rewards)):
                                if rewards[j].get('title'):
                                    title = rewards[j]['title']
                                    local_key = 'ftbquests.chapter.' + prefix + '.quests' + str(i) + '.rewards' + str(
                                        j) + '.title'
                                    new_key_value, new_text = get_snbt_value(local_key, title)
                                    if new_text:
                                        rewards[j]['title'] = new_text
                                    key_value.update(new_key_value)
                                # rewards[j].item.tag
                                if rewards[j].get('item'):
                                    if type(rewards[j]['item']) == 'dict' and rewards[j]['item'].get('tag'):
                                        if type(rewards[j]['item']['tag']) == 'dict' and rewards[j]['item']['tag'].get(
                                                'display'):
                                            if type(rewards[j]['item']['tag']['display']) == 'dict' and \
                                                    rewards[j]['item']['tag']['display'].get('Lore'):
                                                lore = rewards[j]['item']['tag']['display']['Lore']
                                                local_key = 'ftbquests.chapter.' + prefix + '.quests' + str(
                                                    i) + '.rewards' + str(
                                                    j) + '.item.tag.display.Lore'
                                                new_key_value, new_text = get_snbt_value(local_key, lore)
                                                if new_text:
                                                    rewards[j]['item']['tag']['display']['Lore'] = new_text
                                                key_value.update(new_key_value)
                                                rewards[j]['item']['tag']['display']['Lore'] = lore
                                            if rewards[j]['item']['tag']['display'].get('Name'):
                                                name = rewards[j]['item']['tag']['display']['Name']
                                                local_key = 'ftbquests.chapter.' + prefix + '.quests' + str(
                                                    i) + '.rewards' + str(
                                                    j) + '.item.tag.display.Name'
                                                new_key_value, new_text = get_snbt_value(local_key, name)
                                                if new_text:
                                                    rewards[j]['item']['tag']['display']['Name'] = new_text
                                                key_value.update(new_key_value)
            # 寫入更新後的quest
            with open(output_path, 'w', encoding="utf-8") as fout:
                print(TextStyle.GREEN, "\r================", output_path, "snbt替換結束================", TextStyle.RESET)
                fout.write(snbtlib.dumps(quest, compact=LOW))
        except Exception as ex:
            print(TextStyle.RED, f"{i}在翻譯時遇到錯誤:{ex}", TextStyle.RESET)
            continue

    t = list(quest_path.rglob("*.nbt"))
    for i in tqdm(range(0, len(t)), colour='#0396FF'):
        try:
            input_path = t[i]
            output_path = make_output_path(input_path)
            quest = get_nbt_quest(input_path)
            prefix = '' + list(input_path.parts)[-1].replace('.nbt', '')
            # chapter[title,description,text]
            if quest.get('title'):
                local_key = 'ftbquests.chapter.' + prefix + '.title'
                new_key_value = get_nbt_value(local_key, quest['title'])
                key_value.update(new_key_value)
            if quest.get('description'):
                description = quest['description']
                if len(description) > 0:
                    local_key = 'ftbquests.chapter.' + prefix + '.description'
                    new_key_value = get_nbt_value(local_key, quest['description'])
                    key_value.update(new_key_value)
            if quest.get('text'):
                text = quest['text']
                if len(text) > 0:
                    local_key = 'ftbquests.chapter.' + prefix + '.text'
                    new_key_value = get_nbt_value(local_key, quest['text'])
                    key_value.update(new_key_value)

            # chapter.tasks[i][title,description,text]
            if quest.get('tasks'):
                if type(quest['tasks']) == nbt.TAG_List:
                    for i in range(0, len(quest['tasks'])):
                        if quest['tasks'][i].get('title'):
                            local_key = 'ftbquests.chapter.' + prefix + '.tasks' + str(i) + '.title'
                            new_key_value = get_nbt_value(local_key, quest['tasks'][i]['title'])
                            key_value.update(new_key_value)
                        if quest['tasks'][i].get('description'):
                            description = quest['tasks'][i]['description']
                            if len(description) > 0:
                                local_key = 'ftbquests.chapter.' + prefix + '.tasks' + str(i) + '.description'
                                new_key_value = get_nbt_value(local_key, quest['tasks'][i]['description'])
                                key_value.update(new_key_value)
                        if quest['tasks'][i].get('text'):
                            text = quest['tasks'][i]['text']
                            if len(text) > 0:
                                local_key = 'ftbquests.chapter.' + prefix + '.tasks' + str(i) + '.text'
                                new_key_value = get_nbt_value(local_key, quest['tasks'][i]['text'])
                                key_value.update(new_key_value)
            # 寫入更新後的quest
            quest.write_file(output_path)
            print(TextStyle.GREEN, "\r================", output_path, "替換結束================", TextStyle.RESET)
        except Exception as ex:
            print(TextStyle.RED, f"{i}在翻譯時遇到錯誤:{ex}", TextStyle.RESET)
            continue

    # 生成json
    with open('./en_us.json', 'w', encoding="utf-8") as fout:
        fout.write(json.dumps(key_value, indent=1, ensure_ascii=False))
        print("================json生成結束================")
        print(TextStyle.CYAN,
              "鍵值生成格式為【ftbquests.任務部分.任務原文件名稱.區域.區域序號(從0開始)+n*子區域.子區域序號(從0開始)+行號(單行則無)】")
        print("Tip：鍵值後序號不連續可能為有空白行")
        print("關於如何使用此文件有兩種形式:")
        print("1.製作成resourcepack下資源包，可以參考www.mcmod.cn/post/2194.html")
        print("2.製作成kubejs下資源包(依賴kubejs)"
              "可以參考www.reddit.com/r/feedthebeast/comments/qllnpq/how_to_translate_quests_in_a_modpack_and_my/",
              TextStyle.RESET)
