import sys, re, sys, os, requests
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Ui_window import *
from bs4 import BeautifulSoup


class Worker(QThread):
    finished = pyqtSignal(str, str)

    def __init__(self,kw, parent=None):
        self.kw = kw
        super().__init__(parent)

    def run(self):
        # 在子线程中执行耗时操作
        result1, result2 = self.do_something(self.kw)
        # 发送信号，将结果传递给主线程
        self.finished.emit(result1, result2)

    def do_something(self,kw):
        if kw == None or kw == "":
            return "你没有输入内容！",kw
        
        elif kw.strip() == "":

            return "你没有输入内容！",kw
        url = "https://zh.wikipedia.org/w/index.php?search={}&ns0=1".format(str(kw))
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57"
        }
        try:
            return requests.get(url=url, headers=header).text, kw
        except:
            return "网络错误！",kw


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.init_buttom()
        self.textBrowser.anchorClicked.connect(self.new_anchorClicked)

    def new_anchorClicked(self,url):
        kw = str(url.toString()).replace("/wiki/", "")
        self.clean_pannel()
        self.new_print("请稍等，正在搜索“{}”\n".format(str(kw)))
        r = self.new_search(kw)
        if r:
            self.check_r(r, kw)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 用户按下了 Enter 键
            self.go_search()

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    def mouseMoveEvent(self, e: QMouseEvent):
        try:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)
        except:
            pass

    def init_buttom(self):
        self.pushButton_4.clicked.connect(self.page_change_to_search)
        self.pushButton_3.clicked.connect(self.page_change_to_about)
        self.pushButton_2.clicked.connect(self.go_search)

    def go_search(self):
        self.clean_pannel()
        kw = self.lineEdit.text()
        self.new_print("请稍等，正在搜索“{}”\n".format(str(kw)))
        r = self.new_search(kw)
        if r:
            self.check_r(r, kw)


    # def add_to_pannel(self, text):
    #     self.textBrowser.insertHtml(text)

    def clean_pannel(self):
        self.textBrowser.clear()

    def page_change_to_about(self):
        self.stackedWidget.setCurrentIndex(1)

    def page_change_to_search(self):
        self.stackedWidget.setCurrentIndex(0)

    def new_print(self, text):
        # self.textBrowser.appendPlainText(text)
        text = str(text)
        self.textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.textBrowser.insertHtml(text)


    def new_search(self, kw):
        self.worker = Worker(kw)
        self.worker.finished.connect(self.handle_result)
        self.worker.start()

    def handle_result(self, result1, result2):
        # 处理子线程传递过来的结果
        r ,kw = result1, result2
        print(result1, result2)
        self.clean_pannel()
        if r == "你没有输入内容！":
            self.new_print("你没有输入内容！")
        elif r == "网络错误！":
            self.network_error()
        elif r:
            self.check_r(r,kw)


    def search(self,kw):
        if kw == None or kw == "":
            self.new_print("你没有输入内容！")
            return False
        elif kw.strip() == "":
            self.new_print("你没有输入内容！")
            return False
        url = "https://zh.wikipedia.org/w/index.php?search={}&ns0=1".format(str(kw))
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57"
        }
        try:
            return requests.get(url=url, headers=header).text
        except:
            self.network_error()



    def check_r(self, r, kw):
        self.clean_pannel()
        # self.new_print("你搜索的是 “{}”".format(str(kw)))
        if "找不到和查询相匹配的结果。" in r:
            self.new_print("你输的啥东西，找不到相关词条\n")
        elif "搜索结果" in r:
            self.new_print("没有找到完全相同的词条\n")
            # self.new_print("以下是搜索结果：")
            # self.new_print_search_result(r)
        elif " - 维基百科，自由的百科全书" in r:
            self.new_print("找到了完全匹配的词条“{}”\n".format(str(kw)))
            self.new_print("——" * 11)
            self.new_print("\n")
            self.print_introducuion(r)
        else: 
            self.new_print("网页解析失败！")

    def print_introducuion(self, bs):
        # 输出正文
        bs = BeautifulSoup(bs, "html.parser").find("div", {"id": "bodyContent"})
        bs = bs.find(id="mw-content-text")
        bs = bs.find(class_="mw-parser-output")
        bs = bs.find_all("p", recursive=False)
        for i in bs:
            text = i
            # text = re.sub(r'alt=".+?"', '', text)
            self.new_print(text)
        # 回到顶部
        self.textBrowser.verticalScrollBar().setValue(0)

    def network_error(self):
        self.new_print("网络连接错误！")
        self.new_print("请检查代理是否连接")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
