from src import single_instance
from src.app import App


def main():
    # 已經有一份在跑就把它叫到前面，自己安靜退場。跑出兩份會一個在點、一個
    # 顯示暫停，畫面互相矛盾，對頭控使用者非常混亂。
    if not single_instance.acquire():
        single_instance.focus_existing()
        return

    try:
        app = App()
        app.run()
    finally:
        single_instance.release()


if __name__ == "__main__":
    main()
