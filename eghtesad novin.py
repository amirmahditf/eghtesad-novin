""" 

برای استفاده از برنامه قبل از اجرا باید چند کتابخوانه رو نصب کنید که عبارتند از 


pip install scrapy
pip install beautifulsoup4
pip install requests beautifulsoup4 PyQt5


پی از نصب این کتابخوانه ها به صورت کامل برنامه رو اجرا کنید
"""
"""البته این برنامه ممکن است به دلیل نوسانات اینترنتی گاهی اوقات قط شود و برنامه بسته شود که کافی است دوباره برنامه را اجرا کنید

این نوسانات ممکن است در صورت اتصال به وی پی ان یا ضعیفی اینترنت رخ دهد
"""


import sys
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QTextCursor, QColor
url = "https://www.shahrekhabar.com/اقتصاد-نیوز"


def convert_persian_to_english_number(persian_number):
    persian_to_english = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    return persian_number.translate(persian_to_english)


def get_latest_news_times():
    response = requests.get(url)
    if response.status_code != 200:
        print(
            f"Error: Unable to access the site. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    news_list = soup.find("ul", class_="news-list-items clearfix")
    news_items = news_list.find_all("li")

    news_times = []
    for item in news_items:
        time_span = item.find("span", class_="refrence minw80 right")
        if time_span:
            news_times.append(time_span.text.strip())

    return news_times


def parse_time_to_minutes(news_time):
    try:
        parts = news_time.split()
        time_number = int(convert_persian_to_english_number(parts[0]))
        if "دقيقه" in news_time:
            return time_number
        elif "ساعت" in news_time:
            return time_number * 60
        return None
    except:
        print("Error: Unable to parse news time.")
        return None


def get_news_times_in_last_hour(news_times):
    last_hour_times = []

    for news_time in news_times:
        if "دقيقه" in news_time:
            minutes_ago = parse_time_to_minutes(news_time)
            if minutes_ago is not None and minutes_ago <= 60:
                last_hour_times.append(minutes_ago)

    return last_hour_times


class NewsMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.monitor_news)
        self.timer.start(500)

        self.last_news_time = None
        self.last_news_minutes = None
        self.last_upload_error_time = None
        self.initial_news_times_printed = False
        self.last_printed_minutes = 0
        self.error_printed = False

    def initUI(self):
        self.layout = QVBoxLayout()
        self.news_label = QLabel("Last news was uploaded: ")
        self.layout.addWidget(self.news_label)
        self.news_count_label = QLabel("Number of uploads in the last hour: ")
        self.layout.addWidget(self.news_count_label)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)
        self.setWindowTitle('News Monitor')

    def append_text(self, text, color=None):
        self.text_edit.moveCursor(QTextCursor.End)
        if color:
            self.text_edit.setTextColor(color)
        else:
            self.text_edit.setTextColor(QColor(0, 255, 0))
        self.text_edit.insertPlainText(text + "\n")
        self.text_edit.setTextColor(QColor(0, 0, 0))

    def monitor_news(self):
        latest_news_times = get_latest_news_times()

        if latest_news_times:
            latest_news_time = latest_news_times[0]
            latest_news_minutes = parse_time_to_minutes(latest_news_time)

            if latest_news_minutes is not None:
                if self.last_news_time is None:
                    self.news_label.setText(
                        f"Last news was uploaded {latest_news_minutes} minutes ago.")
                    self.news_label.setStyleSheet("color: green;")
                    self.append_text(
                        f"Last news was uploaded {latest_news_minutes} minutes ago.")
                    self.error_printed = False
                elif latest_news_minutes == 0 and self.last_news_minutes != 0:
                    self.news_label.setText(f"New news uploaded just now.")
                    self.news_label.setStyleSheet("color: green;")
                    self.append_text(f"New news uploaded just now.")
                    self.initial_news_times_printed = False
                    self.error_printed = False
                elif latest_news_minutes != self.last_news_minutes:
                    self.news_label.setText(
                        f"Last news was uploaded {latest_news_minutes} minutes ago.")
                    self.news_label.setStyleSheet("color: green;")
                    self.append_text(
                        f"Last news was uploaded {latest_news_minutes} minutes ago.")
                    self.last_upload_error_time = None
                    self.error_printed = False
                elif latest_news_minutes > 15 and latest_news_minutes == self.last_news_minutes:
                    if not self.error_printed:
                        error_message = f"No new uploads for the past {latest_news_minutes} minutes."
                        self.news_label.setText(error_message)
                        self.news_label.setStyleSheet("color: red;")
                        self.append_text(error_message, QColor(255, 0, 0))
                        self.error_printed = True

                self.last_news_time = latest_news_time
                self.last_news_minutes = latest_news_minutes

            current_count = len(get_news_times_in_last_hour(latest_news_times))
            if not self.initial_news_times_printed or current_count != self.last_printed_minutes:
                self.news_count_label.setText(
                    f"Number of uploads in the last hour: {current_count}")
                self.news_count_label.setStyleSheet("color: green;")
                self.append_text(
                    f"Number of uploads in the last hour: {current_count}")
                self.initial_news_times_printed = True
                self.last_printed_minutes = current_count


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NewsMonitor()
    ex.show()
    sys.exit(app.exec_())
