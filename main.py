from func.base import check_config_exists

VERSION = 'v0.0.1'

if __name__ == '__main__':
    try:
        check_config_exists()
        import func
        while True:
            print('============FTBQ繁中化工具-%s============' %VERSION)
            print('主功能引導\n1.翻譯任務snbt\n2.生成lang文件(默認位置config中WORK_PATH)\n3.翻譯lang文件\n4.回填lang文件\n5.退出')
            choice = input('請輸入你要選擇的功能：')
            if choice == '1':
                func.quest_trans()
            elif choice == '2':
                func.trans2lang()
            elif choice == '3':
                func.lang_trans()
            elif choice == '4':
                func.back_fill()
            elif choice == '5':
                break
            else:
                print('無效輸入')
    except Exception as e:
        print("程序發生了錯誤:", repr(e))
    finally:
        input("按任意鍵繼續...")


