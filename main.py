import os
import sys
import yt_dlp
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject
from UI_1 import *

class OutputLogger(QObject):
    emit_write = QtCore.pyqtSignal(str)

    # class Severity:
    #     DEBUG = 0
    #     ERROR = 1

    def __init__(self, io_stream):
        super().__init__()

        self.io_stream = io_stream
        # self.severity = severity

    def write(self, text):
        self.io_stream.write(text)
        self.emit_write.emit(text)
        # self.emit_write.emit(text, self.severity)

    def flush(self):
        self.io_stream.flush()


OUTPUT_LOGGER_STDOUT = OutputLogger(sys.stdout)
OUTPUT_LOGGER_STDERR = OutputLogger(sys.stderr)
# OUTPUT_LOGGER_STDIN = OutputLogger(sys.stdin)

sys.stdout = OUTPUT_LOGGER_STDOUT
sys.stderr = OUTPUT_LOGGER_STDERR
# sys.stdin  = OUTPUT_LOGGER_STDIN


class downloader(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)


    def __init__(self, parent=None):
        super().__init__(parent)
        self.url = None
        self.quality = None
        self.proxy = None
        self.writesubtitles = None
        self.only_audio = None
        self.noplaylist = None
        self.useproxy = None
        self.v_ext = None
        self.a_ext = None
        self.list_format = None

    def list_formats(self):
        ydl_opts = {'listformats': 'all'}
        if self.useproxy == True:
            ydl_opts['proxy'] = '{0}'.format(self.proxy)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # yt_dlp.YoutubeDL(ydl_opts)
                ydl.download([self.url])
        except:
            print("Возникла ошибка, проверьте правильность введенных данных, а так же подключение к интернету")
        else:
            self.mysignal.emit('Процесс завершен!')
        self.mysignal.emit('finish')

    def run(self) -> None:
        if self.list_format == True:
            self.list_formats()
        else:
            ydl_opts = {'format':'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b'}
            self.mysignal.emit('Процесс Скачивания запущен! ...')
            if self.quality != "Авто (лучшее)" and self.v_ext == "Авто" and self.a_ext == "Авто":
                ydl_opts['format'] = 'bv*[height<={0}]+ba/b[height<={0}]'.format(self.quality)
            if self.quality != "Авто (лучшее)" and self.v_ext != "Авто" and self.a_ext != "Авто":
                ydl_opts['format'] = 'bv*[ext={1}][height<={0}]+ba*[ext={2}]/b[height<={0}]'.format(self.quality,self.v_ext,self.a_ext)
            if self.quality != "Авто (лучшее)" and self.v_ext != "Авто" and self.a_ext == "Авто":
                ydl_opts['format'] = 'bv*[ext={1}][height<={0}]+ba/b[height<={0}]'.format(self.quality,self.v_ext)
            if self.quality != "Авто (лучшее)" and self.v_ext == "Авто" and self.a_ext != "Авто":
                ydl_opts['format'] = 'bv*[height<={0}]+ba*[ext={1}]/b[height<={0}]'.format(self.quality,self.a_ext)
            if self.only_audio == True and self.a_ext == "Авто":
                ydl_opts['format'] = 'ba'
            if self.only_audio == True and self.a_ext != "Авто":
                ydl_opts['format'] = 'ba*[ext={0}]/ba'.format(self.a_ext)
            if self.useproxy == True:
                ydl_opts['proxy'] = '{0}'.format(self.proxy)
            if self.writesubtitles == True:
                ydl_opts['writeautomaticsub'] = 'all'
                ydl_opts['writesubtitles'] = 'all'
            if self.noplaylist == True:
                ydl_opts['noplaylist'] = 'yes'
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # yt_dlp.YoutubeDL(ydl_opts)
                    ydl.download([self.url])
            except:
                print("Возникла ошибка, проверьте правильность введенных данных, а так же подключение к интернету")
            else:
                self.mysignal.emit('Процесс скачивания завершен!')

            self.mysignal.emit('finish')

    def init_args(self,link, quality, proxy, writesubtitles, only_audio, noplaylist, useproxy,v_ext,a_ext, list_formats):
        self.url = link
        self.quality = quality
        self.proxy = proxy
        self.writesubtitles = writesubtitles
        self.only_audio = only_audio
        self.noplaylist = noplaylist
        self.useproxy = useproxy
        self.v_ext = v_ext
        self.a_ext = a_ext
        self.list_format = list_formats



class gui(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(gui,self).__init__(parent)


        self.ui = Ui_Downloader()
        self.ui.setupUi(self)


        OUTPUT_LOGGER_STDOUT.emit_write.connect(self.handler)
        OUTPUT_LOGGER_STDERR.emit_write.connect(self.handler)
        # OUTPUT_LOGGER_STDIN.emit_write.connect(self.handler)

        self.setWindowTitle('Multi Platform Video Downloader')
        self.setWindowIcon(QIcon("./images/logo.png"))
        self.setStyleSheet("QMainWindow{\n""background-image:url(./images/Background(900x600).png)\n""}\n""")
        self.resize(900, 600)
        self.setMinimumSize(QtCore.QSize(900, 600))
        self.setMaximumSize(QtCore.QSize(900, 600))
        self.download_folder = None
        self.ui.pushButton_2.clicked.connect(self.get_folder)
        self.ui.pushButton.clicked.connect(self.start)
        self.ui.pushButton_3.clicked.connect(self.list_formats)
        self.mythread = downloader()
        self.mythread.mysignal.connect(self.handler)
        self.ui.comboBox.addItems(["Авто (лучшее)","360", "480",
                        "720", "1080", "1440", "2160"])
        self.ui.comboBox_2.addItems(["Авто", "mp4", "webm",
                                   "flv", "avi", "mkv"])
        self.ui.comboBox_3.addItems(["Авто", "m4a", "aac",
                                   "mp3", "ogg", "opus", "webm"])
        self.ui.comboBox_2.setEnabled(False)
        self.ui.comboBox_3.setEnabled(False)
        self.ui.comboBox.currentTextChanged.connect(self.enable_combo)
        # font = QtGui.QFont()
        # font.setPointSize(6)
        # self.ui.plainTextEdit.setFont(font)

    # def paintEvent(self, event) -> None:
    #     painter = QPainter(self)
    #     pixmap = QPixmap("./logo1_4_3.png")
    #     painter.drawPixmap(self.rect(), pixmap)
    def list_formats(self):
        if len(self.ui.lineEdit.text()) > 5:
                link = self.ui.lineEdit.text()
                quality = None
                v_ext = None
                a_ext = None
                proxy = self.ui.lineEdit_2.text()
                writesubtitles = None
                only_audio = None
                noplaylist = None
                useproxy = self.ui.checkBox.isChecked()
                list_formats = True
                self.mythread.init_args(link, quality, proxy, writesubtitles, only_audio, noplaylist, useproxy, v_ext, a_ext, list_formats)
                self.mythread.start()
                self.locker(True)
        else:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Ссылка на видео не указана')

    def enable_combo(self):
        if self.ui.comboBox.currentText() != "Авто (лучшее)":
            self.ui.comboBox_2.setEnabled(True)
            self.ui.comboBox_3.setEnabled(True)
        else:
            self.ui.comboBox_2.setEnabled(False)
            self.ui.comboBox_3.setEnabled(False)


    def start(self):
        if len(self.ui.lineEdit.text()) > 5:
            if self.download_folder != None and self.download_folder != '':
                link = self.ui.lineEdit.text()
                quality = self.ui.comboBox.currentText()
                v_ext = self.ui.comboBox_2.currentText()
                a_ext = self.ui.comboBox_3.currentText()
                proxy = self.ui.lineEdit_2.text()
                writesubtitles = self.ui.checkBox_2.isChecked()
                only_audio = self.ui.checkBox_3.isChecked()
                noplaylist = self.ui.checkBox_4.isChecked()
                useproxy = self.ui.checkBox.isChecked()
                list_formats = False
                self.mythread.init_args(link, quality,proxy,writesubtitles,only_audio,noplaylist,useproxy,v_ext,a_ext, list_formats)
                self.mythread.start()
                self.locker(True)
            else:
                QtWidgets.QMessageBox.warning(self,'Ошибка','Вы не выбрали папку')
        else: QtWidgets.QMessageBox.warning(self,'Ошибка','Ссылка на видео не указана')

    def get_folder(self):
        self.download_folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выбрать папку для сохранения', './',QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
        if self.download_folder != '':
           os.chdir(self.download_folder)

    # def handler(self, value):
    #     if value == 'finish':
    #         self.locker(False)
    #     else:
    #         self.ui.plainTextEdit.appendPlainText(value)

    def handler(self, text):
        # text = repr(text)
        # if severity == OutputLogger.Severity.ERROR:
        #     text = '<b>{}</b>'.format(text)
        if text == 'finish':
            self.locker(False)
        self.ui.plainTextEdit.appendPlainText(text)


    def locker(self, lock_value):
        base = [self.ui.pushButton,self.ui.pushButton_2, self.ui.pushButton_3]

        for item in base:
            item.setDisabled(lock_value)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = gui()
    # win.setStyleSheet("QMainWindow{\n""background-image:url(./images/Background(900x600).png)\n""}\n""")
    win.show()
    sys.exit(app.exec_())
