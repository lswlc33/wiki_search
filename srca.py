# 这是命令行版本的，仅存档

import requests
from bs4 import BeautifulSoup
import re, sys, os



def write_to_txt(text):
    text = str(text)
    with open("example.html", "w", encoding="utf-8") as f:
        f.write(text)


def check_r(r, kw):
    print("你搜索的是 “{}”".format(str(kw)))
    if "找不到和查询相匹配的结果。" in r:
        print("你输的啥东西，找不到相关词条")
    elif "搜索结果" in r:
        print("以下是搜索结果：")
        print_search_result(r)
    elif " - 维基百科，自由的百科全书" in r:
        print("找到了完全匹配的词条“{}”".format(str(kw)))
        print("#" * 20)
        print_introducuion(r)
    else:
        print("网页解析失败！")
    end_page()


def print_search_result(bs):
    bs = BeautifulSoup(bs, "html.parser").find_all(
        "div", {"class": "mw-search-result-heading"}
    )
    bs = str(bs)
    s_result = re.findall('title="(.*?)"', bs)
    for i in range(len(s_result)):
        print(str(i + 1) + ". " + s_result[i])
    choose_search_result(s_result)


def choose_search_result(result):
    print("#" * 20)
    print("选择你要查看的词条序号")
    num = input("序号：")
    print("#" * 20)
    try:
        num = int(num)
        kw = result[num - 1]
        print("#" * 20)
        print("你选择了第{}项:{}".format(num, kw))
        print("即将为你展示该词条...")
        print("#" * 20)
    except:
        print("请输入正确的序号!")
        choose_search_result(result)
    show_chosen_result(kw)


def show_chosen_result(kw):
    r = search(kw)
    os.system("cls")
    print_introducuion(r)


def end_page():
    print("#" * 20)
    print("1.返回搜索 " "2.退出程序")
    ch = input("选择:")
    if ch == "1":
        main()
    if ch == "2":
        sys.exit()
    else:
        print("输入错误！")
        end_page()


def print_introducuion(bs):
    bs = BeautifulSoup(bs, "html.parser").find("div", {"id": "bodyContent"})
    bs = bs.find(id="mw-content-text")
    bs = bs.find(class_="mw-parser-output")
    bs = bs.find_all("p", recursive=False)
    for i in bs:
        print(i.get_text())


def search(kw):
    if kw.strip() == "":
        print("你没有输入内容！")
        end_page()
    url = "https://zh.wikipedia.org/w/index.php?search={}&ns0=1".format(str(kw))
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57"
    }
    try:
        return requests.get(url=url, headers=header).text
    except:
        network_error()


def network_error():
    print("网络连接错误！")
    print("请检查网络")
    end_page()


def main():
    os.system("cls")
    print("#" * 20)
    print("欢迎使用wiki搜索!")
    print("#" * 20)
    print("请输入要搜索的内容")
    kw = input("搜索：")

    # kw = "56413"
    print("#" * 20)
    print("你搜索的是 “{}”\n正在搜索中...".format(str(kw)))
    print("#" * 20)

    r = search(kw)  # 搜一搜
    os.system("cls")

    check_r(r, kw)  # 看看结果


if __name__ == "__main__":
    main()
