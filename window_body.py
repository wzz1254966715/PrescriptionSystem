import sys
import re
import time
import os
import _sqlite3 as sqlite3
import webbrowser

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, \
    QRadioButton, QMessageBox, QHeaderView, QAbstractItemView, QMainWindow, QAction, QMenu, QDialog
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5 import QtGui, Qt, QtPrintSupport
from PyQt5.QtCore import Qt, QRect


class WindowPrescription(QMainWindow):
    def __init__(self, user_data, drug_data, total_price):
        super().__init__()
        self.a = QWidget(self)
        self.setCentralWidget(self.a)
        self.user_data = user_data
        self.drug_data = drug_data
        self.total_price = total_price
        self.setWindowTitle('中药处方')
        self.setFixedSize(500, 700)

        self.head = QLabel('中药处方笺')
        font_table = QtGui.QFont()
        font_table.setFamily("Microsoft New Tai Lue")
        font_table.setPointSize(29)
        font_table.setBold(True)
        font_label = QtGui.QFont()
        font_label.setPointSize(10)
        font_label.setBold(True)

        self.head.setFont(font_table)
        self.head.setAlignment(Qt.AlignCenter)
        self.name = QLabel('姓名: ' + self.user_data['name'])
        self.name.setFont(font_label)
        self.sex = QLabel('性别: ' + self.user_data['sex'])
        self.sex.setFont(font_label)
        self.age = QLabel('年龄: ' + self.user_data['age'])
        self.age.setFont(font_label)

        self.address = QLabel('住址: ' + self.user_data['address'] + '    ')
        self.address.setFont(font_label)
        times = time.localtime()
        self.times = QLabel('时间: {0}年 {1}月 {2}日'.format(times.tm_year, times.tm_mon, times.tm_mday))
        self.times.setFont(font_label)

        self.say = QLabel('主诉: ')
        self.say.setFont(font_label)
        self.say1 = QLabel(self.user_data['say'])

        self.tongue = QLabel('舌脉: ')
        self.tongue.setFont(font_label)
        self.tongue1 = QLabel(self.user_data['tongue'])

        self.result = QLabel('诊断: ')
        self.result.setFont(font_label)
        self.result1 = QLabel(self.user_data['result'])

        self.doctor = QLabel('医师: 某某某')
        self.setFont(font_label)
        self.price_label = QLabel('总价: ' + str(round(self.total_price, 2)) + ' 元')
        self.price_label.setFont(font_label)

        self.num = QLabel('总数: ' + str(self.user_data['num']) + ' 副')
        self.num.setFont(font_label)

        hLayout_head = QHBoxLayout()
        hLayout_head.addWidget(self.head)

        gridLayout = QGridLayout()
        gridLayout.addWidget(self.name, 0, 0, 1, 1)
        gridLayout.addWidget(self.sex, 0, 2, 1, 1)
        gridLayout.addWidget(self.age, 0, 4, 1, 1)

        gridLayout.addWidget(self.address, 1, 0, 1, 1)
        gridLayout.addWidget(self.times, 1, 2, 1, 2)

        gridLayout.addWidget(self.say, 2, 0, 1, 1)
        gridLayout.addWidget(self.say1, 2, 1, 1, 6)
        gridLayout.addWidget(self.tongue, 3, 0, 1, 1)
        gridLayout.addWidget(self.tongue1, 3, 1, 1, 6)
        gridLayout.addWidget(self.result, 4, 0, 1, 1)

        data_table = QTableWidget()
        data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        data_table.verticalHeader().setVisible(False)
        data_table.horizontalHeader().setVisible(False)
        data_table.setEnabled(False)
        data_table.setGridStyle(Qt.NoPen)
        font_table = QtGui.QFont()
        font_table.setPointSize(15)
        data_table.setFont(font_table)
        data_table.setStyleSheet("color:black")
        data_table.setColumnCount(3)
        row = len(self.drug_data) / 3 + 1
        data_table.setRowCount(row)
        data_table.resize(self.width() - 80, self.height() - 400)
        data_table.setFrameShape(QFrame.NoFrame)
        length = len(self.drug_data)
        for i in range(int(length / 3 + 1)):
            for j in range(3):
                if i * 3 + j >= length:
                    break
                str1 = list(self.drug_data.keys())[i * 3 + j]
                str2 = str(list(self.drug_data.values())[i * 3 + j])
                temp_data = QTableWidgetItem(str1 + 'X' + str2)
                temp_data.setTextAlignment(Qt.AlignCenter)
                data_table.setItem(i, j, temp_data)

        hLayout_table = QHBoxLayout()
        hLayout_table.addWidget(data_table)

        hLayout_price = QHBoxLayout()
        hLayout_price.addWidget(self.num)
        hLayout_price.addWidget(self.price_label)
        hLayout_button = QHBoxLayout()
        hLayout_button.addWidget(self.doctor)
        hLayout_button.addLayout(hLayout_price)

        vLayout = QVBoxLayout()
        vLayout.addLayout(hLayout_head)
        vLayout.addLayout(gridLayout)
        vLayout.addLayout(hLayout_table)
        vLayout.addLayout(hLayout_button)
        self.a.setLayout(vLayout)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menu_right)

    # 打印菜单
    def menu_right(self):
        cmenu = QMenu(self)
        wrAct = cmenu.addAction("打印")
        wrAct2 = cmenu.addAction("保存为图片")
        wrAct.triggered.connect(self.action_func)
        wrAct2.triggered.connect(self.action2_func)
        cmenu.popup(QtGui.QCursor.pos())
        cmenu.show()

    def action_func(self):
        qpmap = QApplication.primaryScreen()
        pix = qpmap.grabWindow(self.winId())
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setPageSize(QtPrintSupport.QPrinter.B6)
        preview = QtPrintSupport.QPrintDialog(printer, self)
        if preview.exec():
            painter = QtGui.QPainter(printer)
            rect = painter.viewport()  # 获取矩形区域大小
            size = pix.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)  # 保证图片显示完整

            painter.setViewport(0, 0, size.width(), size.height())  # 按照图像大小比例重设矩形区域
            rect = QRect(0, 0, pix.width()+50,pix.height())
            painter.setWindow(rect)  # 设置窗口大小
            painter.drawPixmap(30, 0, pix)   # 将图像绘制在Qpainter上
            painter.end()
            conn = sqlite3.connect('./data_a.db')
            for name in list(self.drug_data.keys()):
                c = conn.cursor()
                c.execute("select amount from test_data where name='{0}'".format(name))
                old_amount = c.fetchall()[0][0]
                new_amount = old_amount - self.drug_data[name]
                c.execute("update test_data set amount={0} where name='{1}'".format(new_amount, name))
                conn.commit()
                c.close()
            conn.close()
            self.close()

    def action2_func(self):
        qpmap = QApplication.primaryScreen()
        pix = qpmap.grabWindow(self.winId())
        file = "C:/Users/Administrator/Desktop/处方图/"
        if os.path.exists(file):
            pass
        else:
            os.mkdir(file)
        pix.save(file + self.user_data['name'] + ".jpg")
        self.msg_box = QMessageBox()
        self.msg_box.question(self, "通知", "图片已保存至桌面处方图下" + self.user_data['name'] + ".jpg", QMessageBox.Yes)


class WindowDrug(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.drug_data = {}
        self.total_price = 0
        self.setWindowTitle('选药')
        self.resize(500, 300)

        self.drug_name = QLabel("药品名称:")
        self.drug_amount = QLabel('药品数量')
        self.drug_name_line = QLineEdit()
        self.drug_amount_line = QLineEdit()

        gridLayout = QGridLayout()
        gridLayout.addWidget(self.drug_name, 0, 0, 1, 1)
        gridLayout.addWidget(self.drug_name_line, 0, 1, 1, 1)
        gridLayout.addWidget(self.drug_amount, 1, 0, 1, 1)
        gridLayout.addWidget(self.drug_amount_line, 1, 1, 1, 1)

        self.btn_Y = QPushButton('添加')
        self.btn_Y.clicked.connect(self.btn_Y_func)
        self.btn_Y.setShortcut(Qt.Key_Return)
        self.btn_N = QPushButton('取消')
        self.btn_N.clicked.connect(self.close)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.btn_Y)
        hLayout.addWidget(self.btn_N)

        vLayout = QVBoxLayout()
        vLayout.addLayout(gridLayout)
        vLayout.addLayout(hLayout)

        self.setLayout(vLayout)

    def btn_Y_func(self):
        self.name = self.drug_name_line.text()
        self.msg_box = QMessageBox()
        if self.name != '':
            conn = sqlite3.connect('./data_a.db')
            c = conn.cursor()
            c.execute("select * from test_data where name='{0}';".format(self.name))
            value = c.fetchall()
            if len(value):
                self.amount = self.drug_amount_line.text()
                if self.amount != '':
                    if re.search(r'[^\d]', self.amount) is None:
                        self.amount = int(self.amount)
                        amount_sum = self.amount * int(self.user_data['num'])
                        if amount_sum <= value[0][1]:
                            self.drug_data[self.name] = self.amount
                            self.price = float(value[0][2])
                            self.total_price += self.price * amount_sum
                            conn.commit()
                            self.drug_name_line.setText('')
                            self.drug_amount_line.setText('')
                            self.btn_Y.setText('继续添加')
                            self.btn_N.setText('完成')
                            self.btn_N.clicked.connect(self.btn_N_new_func)
                        else:
                            self.msg_box.warning(self, '警告', '库存不足')
                    else:
                        self.msg_box.warning(self, '警告', '药品数量只能为整数')
                else:
                    self.msg_box.warning(self, '警告', '药品数量不能为空')
            else:
                self.msg_box.warning(self, '警告', '查无此药')
            conn.close()
        else:
            self.msg_box.warning(self, '警告', '名称不能为空')

    def btn_N_new_func(self):
        self.win = WindowPrescription(self.user_data, self.drug_data, self.total_price)
        self.win.show()
        self.close()


class WindowDel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('删除药品')
        self.setFixedSize(500, 300)
        self.drugname = QLabel('药品名称:')
        self.drugname_line = QLineEdit()

        self.btn_Y = QPushButton('删除')
        self.btn_Y.setFixedHeight(40)
        self.btn_Y.setShortcut(Qt.Key_Return)
        self.btn_Y.clicked.connect(self.btn_Y_func)
        self.btn_N = QPushButton('取消')
        self.btn_N.setFixedHeight(40)
        self.btn_N.clicked.connect(self.close)

        gridLayout = QGridLayout()
        gridLayout.addWidget(self.drugname, 0, 0, 1, 1)
        gridLayout.addWidget(self.drugname_line, 0, 1, 1, 1)

        dlgLayout = QVBoxLayout()
        dlgLayout.setContentsMargins(40, 40, 40, 40)
        dlgLayout.addLayout(gridLayout)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btn_Y)
        btnLayout.addWidget(self.btn_N)

        dlgLayout.addLayout(btnLayout)

        self.setLayout(dlgLayout)

    def btn_Y_func(self):
        self.name = self.drugname_line.text()
        self.msg_box = QMessageBox()
        if self.name != 0:
            conn = sqlite3.connect('./data_a.db')
            c = conn.cursor()
            sql = "select name from test_data where name='{0}';".format(self.name)
            c.execute(sql)
            value = c.fetchall()
            if len(value) != 0:
                reply = self.msg_box.question(self, '信息', '确定删除名称为{0}的药品信息吗?'.format(self.name))
                if reply == QMessageBox.Yes:
                    sql = "delete from test_data where name='{0}';".format(self.name)
                    c.execute(sql)
                    conn.commit()
                    self.btn_Y.setText('继续删除')
                    self.btn_N.setText('完成')
                else:
                    pass
                self.drugname_line.setText('')
            else:
                self.msg_box.warning(self, '警告', '查无此项')
            conn.close()
        else:
            self.msg_box.warning(self, '警告', '名称不能为空')


class WindowAlter(QWidget):
    def __init__(self, flag):
        super().__init__()
        self.flag = flag
        self.setWindowTitle('修改药品信息')
        self.setFixedSize(500, 300)
        self.drugname = QLabel('药品名称:')
        self.drug_new_name = QLabel('新名称:')
        self.drugamount = QLabel('新数量:')
        self.drugprice = QLabel('新单价:')

        self.drugname_line = QLineEdit()
        self.drug_new_name_line = QLineEdit()
        self.drugamount_line = QLineEdit()
        self.drugprice_line = QLineEdit()

        self.btn_Y = QPushButton('修改')
        self.btn_Y.setFixedHeight(40)
        self.btn_Y.setShortcut(Qt.Key_Return)
        self.btn_Y.clicked.connect(self.btn_Y_func)
        self.btn_N = QPushButton('取消')
        self.btn_N.setFixedHeight(40)
        self.btn_N.clicked.connect(self.close)

        gridLayout = QGridLayout()
        gridLayout.addWidget(self.drugname, 0, 0, 1, 1)
        gridLayout.addWidget(self.drugname_line, 0, 1, 1, 1)

        if self.flag == 0:
            gridLayout.addWidget(self.drug_new_name, 1, 0, 1, 1)
            gridLayout.addWidget(self.drug_new_name_line, 1, 1, 1, 1)
        if self.flag == 1:
            gridLayout.addWidget(self.drugamount, 1, 0, 1, 1)
            gridLayout.addWidget(self.drugamount_line, 1, 1, 1, 1)
        if self.flag == 2:
            gridLayout.addWidget(self.drugprice, 1, 0, 1, 1)
            gridLayout.addWidget(self.drugprice_line, 1, 1, 1, 1)

        dlgLayout = QVBoxLayout()
        dlgLayout.setContentsMargins(40, 40, 40, 40)
        dlgLayout.addLayout(gridLayout)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btn_Y)
        btnLayout.addWidget(self.btn_N)

        dlgLayout.addLayout(btnLayout)

        self.setLayout(dlgLayout)

    def btn_Y_func(self):
        self.msg_box = QMessageBox()
        self.name = self.drugname_line.text()
        if self.name != '':
            if self.flag == 0:
                self.new_name = self.drug_new_name_line.text()
                if self.new_name != '':
                    conn = sqlite3.connect('./data_a.db')
                    c = conn.cursor()
                    sql = "select * from test_data where name='{0}';".format(self.name)
                    c.execute(sql)
                    value = c.fetchall()
                    if len(value) != 0:
                        sql1 = "select * from test_data where name='{0}';".format(self.new_name)
                        c.execute(sql1)
                        value_new = c.fetchall()
                        if len(value_new) == 0:
                            str = "确定将名称为{0}的药品修改为{1}吗?".format(self.name, self.new_name)
                            reply = self.msg_box.question(self, '信息', str, QMessageBox.Yes | QMessageBox.No,
                                                          QMessageBox.No)
                            if reply == QMessageBox.Yes:
                                self.amount = value[0][1]
                                self.price = value[0][2]
                                sql = "delete from test_data where name='{0}';".format(self.name)
                                c.execute(sql)
                                sql = "insert into test_data(name,amount,price)values('{0}',{1},{2});".format(
                                    self.new_name, self.amount, self.price)
                                c.execute(sql)
                                conn.commit()
                                self.btn_Y.setText('继续修改')
                                self.btn_N.setText('完成')
                            else:
                                pass
                            self.drug_new_name_line.setText('')
                            self.drugname_line.setText('')
                        else:
                            self.msg_box.warning(self, '通知', '药品名称重复')
                    else:
                        self.msg_box.warning(self, '通知', '查无此项')
                    conn.close()
                else:
                    self.msg_box.warning(self, '警告', '名称不能为空')
            elif self.flag == 1:
                self.amount = self.drugamount_line.text()
                if self.amount != '':
                    if re.search(r'[^\d]', self.amount) is None:
                        str = "确定将名称为{0}的药品数量修改为{1}包吗?".format(self.name, self.amount)
                        reply = self.msg_box.question(self, '信息', str, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            conn = sqlite3.connect('./data_a.db')
                            c = conn.cursor()
                            sql = "update test_data set amount={0} where name='{1}';".format(self.amount, self.name)
                            c.execute(sql)
                            conn.commit()
                            conn.close()
                            self.btn_Y.setText('继续修改')
                            self.btn_N.setText('完成')
                        else:
                            pass
                        self.drugamount_line.setText('')
                        self.drugname_line.setText('')
                    else:
                        self.msg_box.warning(self, '警告', '数量必须为整数')
                else:
                    self.msg_box.warning(self, '警告', '数量不能为空')
            elif self.flag == 2:
                self.price = self.drugprice_line.text()
                if self.price != '':
                    if (re.search(r'[^\d\.]', self.price) is None) and (len(re.findall(r'\.', self.price)) <= 1):
                        str = "确定将名称为{0}的药品单价修改为{1}元?".format(self.name, self.price)
                        reply = self.msg_box.question(self, '信息', str, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            conn = sqlite3.connect('./data_a.db')
                            c = conn.cursor()
                            sql = "update test_data set price={0} where name='{1}';".format(self.price, self.name)
                            c.execute(sql)
                            conn.commit()
                            conn.close()
                            self.btn_Y.setText('继续修改')
                        else:
                            pass
                        self.drugprice_line.setText('')
                        self.drugname_line.setText('')
                    else:
                        self.msg_box.warning(self, '警告', '价格格式不正确')
                else:
                    self.msg_box.warning(self, '警告', '价格不能为空')
        else:
            self.msg_box.warning(self, '警告', '名称不能为空')


class WindowAdd(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('添加药品')
        self.setFixedSize(500, 300)
        self.drugname = QLabel('药品名称:')
        self.drugamount = QLabel('药品数量:')
        self.drugprice = QLabel('药品单价:')

        self.drugname_line = QLineEdit()
        self.drugamount_line = QLineEdit()
        self.drugprice_line = QLineEdit()

        self.btn_Y = QPushButton('添加')
        self.btn_Y.setFixedHeight(40)
        self.btn_Y.setShortcut(Qt.Key_Return)
        self.btn_Y.clicked.connect(self.btn_Y_func)
        self.btn_N = QPushButton('取消')
        self.btn_N.setFixedHeight(40)
        self.btn_N.clicked.connect(self.close)

        gridLayout = QGridLayout()
        gridLayout.addWidget(self.drugname, 0, 0, 1, 1)
        gridLayout.addWidget(self.drugname_line, 0, 1, 1, 1)

        gridLayout.addWidget(self.drugamount, 1, 0, 1, 1)
        gridLayout.addWidget(self.drugamount_line, 1, 1, 1, 1)

        gridLayout.addWidget(self.drugprice, 2, 0, 1, 1)
        gridLayout.addWidget(self.drugprice_line, 2, 1, 1, 1)

        dlgLayout = QVBoxLayout()
        dlgLayout.setContentsMargins(40, 40, 40, 40)
        dlgLayout.addLayout(gridLayout)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btn_Y)
        btnLayout.addWidget(self.btn_N)

        dlgLayout.addLayout(btnLayout)

        self.setLayout(dlgLayout)

    def btn_Y_func(self):
        self.name = self.drugname_line.text()
        self.amount = self.drugamount_line.text()
        self.price = self.drugprice_line.text()
        recp1 = re.compile(r'[^\d\.]')
        recp2 = re.compile(r'\.')
        if (self.name != '') and (self.amount != '') and (self.price != ''):
            if (re.search(recp1, self.amount) is None) and (re.search(recp1, self.price) is None) and (
                    len(re.findall(recp2, self.amount)) == 0) and (len(re.findall(recp2, self.price)) <= 1):
                self.drugname_line.setText('')
                self.drugamount_line.setText('')
                self.drugprice_line.setText('')
                self.btn_Y.setText('继续添加')
                self.btn_N.setText('完成')
                conn = sqlite3.connect('./data_a.db')
                c = conn.cursor()
                c.execute("select * from test_data where name='{0}'".format(self.name))
                value = c.fetchall()
                if len(value):
                    sql1 = "select amount from test_data where name='{0}';".format(self.name)
                    c.execute(sql1)
                    self.amount = str(int(self.amount) + c.fetchall()[0][0])
                    sql = "update test_data set amount={0},price={1} where name='{2}';".format(self.amount, self.price,
                                                                                               self.name)
                    c.execute(sql)
                else:
                    sql = "insert into test_data(name,amount,price)values('{0}',{1},{2});".format(self.name,
                                                                                                  self.amount,
                                                                                                  self.price)
                    c.execute(sql)
                conn.commit()
                conn.close()
            else:
                self.msg_box = QMessageBox()
                self.msg_box.warning(self, '警告', '单价或数量格式不正确')
        else:
            self.msg_box = QMessageBox()
            self.msg_box.warning(self, '警告', '信息不能为空')


class WindowPatientInfo(QWidget):
    """
        患者信息类
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('患者信息填写')
        self.setFixedSize(500, 600)
        self.username = QLabel(' *    姓名:')
        self.usersex = QLabel('      性别:')
        self.userage = QLabel('      年龄:')
        self.useraddress = QLabel('      地址:')
        self.usersay = QLabel('      主诉')
        self.usertongue = QLabel('      舌脉:')
        self.userresult = QLabel('  诊断结果:')
        self.num = QLabel(' * 药数(副): ')
        self.information = QLabel('* 为必填项')

        self.username_line = QLineEdit()
        self.usersex_radio1 = QRadioButton('男')
        self.usersex_radio1.setChecked(True)
        self.usersex_radio2 = QRadioButton('女')
        self.userage_line = QLineEdit()
        self.useraddress_line = QLineEdit()
        self.usersay_line = QLineEdit()
        self.usertongue_line = QLineEdit()
        self.userresult_line = QLineEdit()
        self.num_line = QLineEdit()

        gridLayout = QGridLayout()
        gridLayout.addWidget(self.username, 0, 0, 1, 1)
        gridLayout.addWidget(self.username_line, 0, 1, 1, 1)

        gridLayout.addWidget(self.usersex, 1, 0, 1, 1)

        radioLayout = QHBoxLayout()
        radioLayout.addWidget(self.usersex_radio1)
        radioLayout.addWidget(self.usersex_radio2)
        gridLayout.addLayout(radioLayout, 1, 1, 1, 1)

        gridLayout.addWidget(self.userage, 2, 0, 1, 1)
        gridLayout.addWidget(self.userage_line, 2, 1, 1, 1)

        gridLayout.addWidget(self.useraddress, 3, 0, 1, 1)
        gridLayout.addWidget(self.useraddress_line, 3, 1, 1, 1)

        gridLayout.addWidget(self.usersay, 4, 0, 1, 1)
        gridLayout.addWidget(self.usersay_line, 4, 1, 1, 1)

        gridLayout.addWidget(self.usertongue, 5, 0, 1, 1)
        gridLayout.addWidget(self.usertongue_line, 5, 1, 1, 1)

        gridLayout.addWidget(self.userresult, 6, 0, 1, 1)
        gridLayout.addWidget(self.userresult_line, 6, 1, 1, 1)

        gridLayout.addWidget(self.num, 7, 0, 1, 1)
        gridLayout.addWidget(self.num_line, 7, 1, 1, 1)

        gridLayout.addWidget(self.information, 8, 0, 1, 1)

        dlglayout = QVBoxLayout()
        dlglayout.setContentsMargins(40, 40, 40, 40)
        dlglayout.addLayout(gridLayout)

        # 确定取消按钮
        self.btn_Y = QPushButton('确定', self)
        self.btn_Y.setFixedHeight(40)
        self.btn_Y.setShortcut(Qt.Key_Return)
        self.btn_Y.clicked.connect(self.btn_Y_func)
        self.btn_N = QPushButton('取消', self)
        self.btn_N.setFixedHeight(40)
        self.btn_N.clicked.connect(self.close)

        btnlayout = QHBoxLayout()
        btnlayout.setSpacing(60)
        btnlayout.addWidget(self.btn_Y)
        btnlayout.addWidget(self.btn_N)

        dlglayout.addLayout(btnlayout)
        self.setLayout(dlglayout)

        self.user_dict = {}

    def btn_Y_func(self):
        self.name = self.username_line.text()
        self.number = self.num_line.text()
        if self.name != '' and self.number != '':
            if re.search(r"[^\d]", self.number) is None:
                self.user_dict = {
                    'name': self.name,
                    'sex': '男' if self.usersex_radio1.isChecked() else '女',
                    'age': self.userage_line.text(),
                    'address': self.useraddress_line.text(),
                    'say': self.usersay_line.text(),
                    'tongue': self.usertongue_line.text(),
                    'result': self.userresult_line.text(),
                    'num': int(self.number)
                }
                # 创建处方窗口,并关闭本窗口
                self.win = WindowDrug(self.user_dict)
                self.win.show()
                self.close()
            else:
                self.msg_box = QMessageBox()
                self.msg_box.warning(self, '警告', '药品副数只能为整数')
        else:
            self.msg_box = QMessageBox()
            self.msg_box.warning(self, '警告', '姓名和药品副数不能为空')

    def __response(self):
        if self.user_dict is not None:
            return self.user_dict


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('中药处方管理系统 V1.0')
        # 设置窗口大小
        desktop = QApplication.desktop()
        desktop_rect = desktop.screenGeometry()
        self.move(0, 0)
        self.resize(desktop_rect.width(), desktop_rect.height() - 80)

    def window_frist_page(self):
        """
            菜单栏
        """

        # 创建菜单栏
        menuBar = self.menuBar()
        self.imAct_wr = menuBar.addAction('开处方')
        self.imAct_wr.triggered.connect(self.action_write_func)
        self.editMenu = menuBar.addMenu('编辑')
        # 编辑子菜单
        self.imAct_add = QAction('添加', self)
        self.imAct_add.triggered.connect(self.action_add_func)
        self.editMenu.addAction(self.imAct_add)
        # 编辑->修改子菜单
        self.Menu_alt = QMenu('修改', self)
        self.imAct_alt_name = QAction('修改名称', self)
        self.imAct_alt_name.triggered.connect(self.action_alt_name_func)
        self.Menu_alt.addAction(self.imAct_alt_name)
        self.imAct_alt_amount = QAction('修改库存数量', self)
        self.imAct_alt_amount.triggered.connect(self.action_alt_amount_func)
        self.Menu_alt.addAction(self.imAct_alt_amount)
        self.imAct_alt_price = QAction('修改单价', self)
        self.imAct_alt_price.triggered.connect(self.action_alt_price_func)
        self.Menu_alt.addAction(self.imAct_alt_price)
        self.editMenu.addMenu(self.Menu_alt)

        self.imAct_del = QAction('删除', self)
        self.imAct_del.triggered.connect(self.action_del_func)
        self.editMenu.addAction(self.imAct_del)

        self.selMenu = menuBar.addMenu('查询')
        # 查询子菜单
        self.imAct_sel_stock = QAction('库存紧张查询', self)
        self.imAct_sel_stock.triggered.connect(self.action_stock_func)
        self.selMenu.addAction(self.imAct_sel_stock)

        # 刷新一下
        self.imAct_refresh = QAction('刷新一下', self)
        self.imAct_refresh.triggered.connect(self.action_refresh_func)
        menuBar.addAction(self.imAct_refresh)

        # 帮助
        self.imAct_help = QAction('帮助', self)
        self.imAct_help.triggered.connect(self.action_help_func)
        menuBar.addAction(self.imAct_help)

        # 搜索按钮
        self.btn_sel = QPushButton('搜索', self)
        self.btn_sel.setCheckable(True)
        self.btn_sel.resize(90, 35)
        self.btn_sel.move(self.width() - self.btn_sel.width() - 20, menuBar.height())
        self.btn_sel.clicked.connect(self.button_search_func)
        # 搜索框
        self.search_bar = QLineEdit(self)
        self.search_bar.resize(200, 35)
        self.search_bar.move(self.width() - self.btn_sel.width() - self.search_bar.width() - 20, menuBar.height())

        # 首页药品信息显示
        self.table_widet = QTableWidget(self)
        self.table_widet.resize(self.width() - self.search_bar.width() - self.btn_sel.width() - 30,
                                self.height() - menuBar.height())
        self.table_widet.move(0, menuBar.height())
        self.table_widet.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widet.setEditTriggers(QAbstractItemView.NoEditTriggers)
        sql = 'select * from test_data'
        self.__table_widget_func(sql)

        # 设置最大化
        self.setWindowState(Qt.WindowMaximized)

    # 写处方
    def action_write_func(self):
        # 患者信息弹窗
        self.paitient_window = WindowPatientInfo()
        self.paitient_window.show()

    # 添加药品
    def action_add_func(self):
        # 添加药品弹窗
        self.win_add = WindowAdd()
        self.win_add.show()

    # 查询库存
    def action_stock_func(self):
        # 显示库存紧张药品
        sql = "select * from test_data where amount<50 order by amount asc"
        self.__table_widget_func(sql)

    # 刷新
    def action_refresh_func(self):
        self.__table_widget_func("select * from test_data")

    # 修改名称
    def action_alt_name_func(self):
        self.win_alt = WindowAlter(0)
        self.win_alt.show()

    # 修改数量
    def action_alt_amount_func(self):
        self.win_alt = WindowAlter(1)
        self.win_alt.show()

    # 修改单价
    def action_alt_price_func(self):
        self.win_alt = WindowAlter(2)
        self.win_alt.show()

    # 删除
    def action_del_func(self):
        self.win_del = WindowDel()
        self.win_del.show()

    def action_help_func(self):
        webbrowser.open_new_tab("help.html")

    # 搜索点击
    def button_search_func(self):
        self.btn_sel.setChecked(False)
        self.search = self.search_bar.text()
        if self.search != '':
            sql = "select * from test_data where name='{0}'".format(self.search)
            self.__table_widget_func(sql)
        else:
            pass
        self.search_bar.setText('')

    # 搜索
    def __table_widget_func(self, sql):
        conn = sqlite3.connect('./data_a.db')
        c = conn.cursor()
        c.execute(sql)
        self.rows = c.fetchall()
        if len(self.rows) == 0:
            c.execute("select * from test_data")
            value = c.fetchall()
            # 防止药库无药时弹出警告框
            if len(value):
                self.msg_box = QMessageBox()
                self.msg_box.warning(self, "警告", "查无此项")
                self.rows = value
            else:
                pass
        else:
            pass
        self.row = len(self.rows)
        if self.row != 0:
            self.col = len(self.rows[0])
        else:
            self.col = 0
        c.close()
        conn.close()
        self.table_widet.setRowCount(self.row)
        self.table_widet.setColumnCount(self.col)
        self.col_name = ['药品名称', '药品数量(包)', '药品单价(元)']
        self.table_widet.setHorizontalHeaderLabels(self.col_name)
        items = QTableWidgetItem()
        items.setTextAlignment(Qt.AlignHCenter)

        for i in range(self.row):
            for j in range(self.col):
                temp_data = QTableWidgetItem(str(self.rows[i][j]))
                temp_data.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table_widet.setItem(i, j, temp_data)


app = QApplication(sys.argv)
win = Window()
win.window_frist_page()
win.show()
sys.exit(app.exec())
