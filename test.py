import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class SQLInjectionScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

    def get_forms(self, url):
        soup = BeautifulSoup(self.session.get(url).content, "html.parser")
        return soup.find_all("form")

    def form_details(self, form):
        detailsOfForm = {}
        action = form.attrs.get("action", "").lower()
        method = form.attrs.get("method", "get").lower()
        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            input_value = input_tag.attrs.get("value", "")
            inputs.append({"type": input_type, "name": input_name, "value": input_value})
        detailsOfForm["action"] = action
        detailsOfForm["method"] = method
        detailsOfForm["inputs"] = inputs
        return detailsOfForm

    def vulnerable(self, response):
        errors = {"quoted string not properly terminated",
                  "unclosed quotation mark after the character string",
                  "you have an error in your sql syntax;"}

        for error in errors:
            if error in response.content.decode().lower():
                return True
        return False

    def sql_injection_scan(self, url):
        if not self.is_valid_url(url):
            error = True
            status = False
            forms = 0
            url = ""
            return status,forms, url, error

        forms = self.get_forms(url)

        for form in forms:
            details = self.form_details(form)

            for c in "\"'":
                data = {}

                for input_tag in details["inputs"]:
                    if input_tag["type"] == "hidden" or input_tag["value"]:
                        data[input_tag["name"]] = input_tag["value"] + c
                    elif input_tag["type"] != "submit":
                        data[input_tag["name"]] = f"test{c}"
                target_url = urljoin(url, details["action"])

                if details["method"] == "post":
                    res = self.session.post(target_url, data=data)
                elif details["method"] == "get":
                    res = self.session.get(target_url, params=data)
                if self.vulnerable(res):
                    status = True
                    error = False
                    print(f"[+] Detected {len(forms)} forms on {url}.")
                    print("SQL Injection attack vulnerability detected in link:", target_url)
                    return status, len(forms), target_url, error
                else:
                    status = False
                    error = False
                    print(f"[+] Detected {len(forms)} forms on {url}.")
                    return status, len(forms), target_url, error

    def is_valid_url(self, url):
        # Regular expression for validating URLs
        pattern = r'^https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[a-zA-Z0-9-._/?]*)?$'
        return re.match(pattern, url) is not None

if __name__ == "__main__":
    url_arg = "https://www.geeksforgeeks.org/python-programming-language/"
    scanner = SQLInjectionScanner()
    scanner.sql_injection_scan(url_arg)
