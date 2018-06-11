import sys
import requests
import xml.etree.ElementTree as et
from selenium import webdriver
from time import sleep
from selenium.webdriver.firefox.options import Options


class Xml:
    amazon_url = None
    login_id = None
    login_pass = None
    line_api_token = None
    line_api_url = None
    purchase_history_Url = None


# setting.xml(設定ファイル)を読み込む
def read_xml():
    FILE_NAME = "setting.xml"
    tree = et.parse(FILE_NAME)
    root = tree.getroot()
    executeFlg = int(root.find('executeFlg').text)

    if executeFlg != 1:
        return False
    else:
        Xml.amazon_url = root.find('amazonUrl').text
        Xml.login_id = root.find('loginId').text
        Xml.login_pass = root.find('loginPassword').text
        Xml.line_api_token = root.find('lineApiToken').text
        Xml.line_api_url = root.find('lineApiUrl').text
        Xml.purchase_history_Url = root.find('purchaseHistoryUrl').text
        return True


# バーチャルダッシュボタンを押下して商品を購入する
def dash_button():
    try:
        options = Options()
        options.set_headless()
        driver = webdriver.Firefox(firefox_options=options)
        #driver = webdriver.Firefox()
        driver.get(Xml.amazon_url)

        # ログイン画面に遷移
        driver.find_element_by_css_selector('#nav-link-accountList').click()

        # メールアドレスを入力する
        driver.find_element_by_css_selector('#ap_email').send_keys(Xml.login_id)
        driver.find_element_by_css_selector('#continue').click()

        # パスワードを入力する
        driver.find_element_by_css_selector('#ap_password').send_keys(Xml.login_pass)
        driver.find_element_by_css_selector('#signInSubmit').click()

        # バーチャルダッシュボタンの要素とボタンに表示されている名前を取得
        button_name = driver.find_element_by_css_selector('span.digital-dash-button-name').text
        digital_dash_button = driver.find_element_by_css_selector('.digital-dash-button-button')

        # バーチャルダッシュボタンを押下する
        # 一度目のボタン押下後に待機時間を挟まないとダブルクリック状態となってしまい、注文確定ができない
        for i in range(2):
            digital_dash_button.click()
            sleep(0.3)

    except Exception:
        button_name = None
        return button_name

    return button_name


def line_notify(button_name):
    if button_name is None:
        message = "バーチャルダッシュ自動化スクリプトの実行に失敗しました"
        stickerPackageId = 1
        stickerId = 113
    else:
        message = "\nバーチャルダッシュ(" + button_name + ")から商品の購入が完了しました\n注文履歴を見る\n" + Xml.purchase_history_Url
        stickerPackageId = 2
        stickerId = 179

    payload = {"message": message, 'stickerPackageId': stickerPackageId, 'stickerId': stickerId}
    headers = {"Authorization": "Bearer " + Xml.line_api_token}
    requests.post(Xml.line_api_url, data=payload, headers=headers)


if __name__ == '__main__':
    if read_xml() is False:
        sys.exit()
    else:
        dash_button_name = dash_button()
        line_notify(dash_button_name)
