# -*- coding: utf-8 -*-
import sys
import requests
import xml.etree.ElementTree as et
from selenium import webdriver
from time import sleep
from selenium.webdriver.firefox.options import Options


class AutoDash:

    def __init__(self):
        # 設定ファイル名
        self.SETTING_FILE_NAME = "setting.xml"
        # 実行フラグ
        self.exe_flg = self.read_xml(self.SETTING_FILE_NAME)
        # オートダッシュボタン押下回数
        self.push_num_of_times = 2
        # 1回目のオートダッシュボタン押下と2回目の間隔
        self.push_interval_time = 0.3

    @classmethod
    def read_xml(cls, file_name):
        """
        setting.xmlを読み込む

        :param: file_name(str)
        :return: 実行するか否か(bool)
        """
        # setting.xml(設定ファイル)を読み込む
        tree = et.parse(file_name)
        root = tree.getroot()
        execute_flg = int(root.find('executeFlg').text)

        if execute_flg != 1:
            return False
        else:
            cls.amazon_url = root.find('amazonUrl').text
            cls.login_id = root.find('loginId').text
            cls.login_pass = root.find('loginPassword').text
            cls.line_api_token = root.find('lineApiToken').text
            cls.line_api_url = root.find('lineApiUrl').text
            cls.purchase_history_Url = root.find('purchaseHistoryUrl').text
            return True

    # バーチャルダッシュボタンを押下して商品を購入する
    def dash_button(self):

        try:
            options = Options()
            options.set_headless()
            driver = webdriver.Firefox(firefox_options=options)
            # driver = webdriver.Firefox()
            driver.get(self.amazon_url)

            # ログイン画面に遷移
            driver.find_element_by_css_selector('#nav-link-accountList').click()

            # メールアドレスを入力する
            driver.find_element_by_css_selector('#ap_email').send_keys(self.login_id)
            driver.find_element_by_css_selector('#continue').click()

            # パスワードを入力する
            driver.find_element_by_css_selector('#ap_password').send_keys(self.login_pass)
            driver.find_element_by_css_selector('#signInSubmit').click()

            # バーチャルダッシュボタンの要素とボタンに表示されている名前を取得
            button_name = driver.find_element_by_css_selector('span.digital-dash-button-name').text
            digital_dash_button = driver.find_element_by_css_selector('.digital-dash-button-button')

            # バーチャルダッシュボタンを押下する
            # 一度目のボタン押下後に待機時間を挟まないとダブルクリック状態となってしまい、注文確定ができない
            for i in range(self.push_num_of_times):
                digital_dash_button.click()
                sleep(self.push_interval_time)

        except Exception:
            button_name = None
            return button_name

        return button_name

    def line_notify(self, button_name):
        if button_name is None:
            message = "バーチャルダッシュ自動化スクリプトの実行に失敗しました"
            stickerPackageId = 1
            stickerId = 113
        else:
            message = "\nバーチャルダッシュ(" + button_name + ")から商品の購入が完了しました\n注文履歴を見る\n" + self.purchase_history_Url
            stickerPackageId = 2
            stickerId = 179

        payload = {"message": message, 'stickerPackageId': stickerPackageId, 'stickerId': stickerId}
        headers = {"Authorization": "Bearer " + self.line_api_token}
        requests.post(self.line_api_url, data=payload, headers=headers)


if __name__ == '__main__':
    auto_dash = AutoDash()
    if auto_dash.exe_flg is False:
        sys.exit()
    else:
        dash_button_name = auto_dash.dash_button()
        auto_dash.line_notify(dash_button_name)
