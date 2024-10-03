import re
import os
import json
from playwright.sync_api import Page


def extract_domain(url):
    try:
        if url:
            # Remove 'https:' or 'http:' if present
            if url.startswith('http:') or url.startswith('https:'):
                url = re.sub(r'^https?:', '', url)
            url =  url.replace('//','')
            # Extract the domain name
            domain = url.split('/')[0]
            return domain if domain else None
    except Exception as e:
        print(f"found error {e}")


def refine_url(url):
    try:
        if url:
            # Remove 'https:' or 'http:' if present
            if url.startswith('http:') or url.startswith('https:'):
                url = re.sub(r'^https?:', '', url)
            url = url.replace('//', 'https://')
            # Extract the domain name
            return url if url else None
    except Exception as e:
        print(f"found error {e}")



class PageInstance:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, url):
        self.page.goto(url)

    @staticmethod
    def safe_get_attribute(element, attribute_name):
        try:
            value = element.get_attribute(attribute_name)
            if value:
                # Encode the value to handle any special characters
                return value.encode('utf-8').decode('utf-8')
            return None
        except Exception as e:
            print(f"Error getting attribute '{attribute_name}': {e}")
            return None


    def wait_for_page_load(self):
        try:
            self.page.wait_for_load_state('networkidle')
        except Exception as e:
            return f"error: {e}"

    def wait_for_time(self, timeout):
        try:
            self.page.wait_for_timeout(timeout)
        except Exception as e:
            return f"error: {e}"

    def accept_cookies(self, cookie_selector):
        try:
            self.page.locator(cookie_selector).click()
            print("Accepted cookies")
        except Exception as e:
            print(f"Could not find or click cookie button: {e}")

    def close_email_signup_popup(self, popup_selector):
        try:
            self.page.locator(popup_selector).click()
            print("Closed email signup popup")
        except Exception as e:
            print(f"Could not find or close the email signup popup: {e}")

    def close_page(self):
        self.page.close()


    def get_images_data(self):
        try:
            """
            Find all images on the page, return a list of dictionaries containing:
            - image name (from src or filename)
            - alt text
            - image URL
            """
            self.wait_for_page_load()
            images = []
            footer = self.page.query_selector('footer')

            # Get all image elements on the page
            img_elements = self.page.query_selector_all('img')
            for img in img_elements:
                # Skip images in the footer
                if footer and footer.query_selector(f'img[src="{img.get_attribute("src")}"]'):
                    continue

                image_url = self.safe_get_attribute(img,"src")
                img_url = refine_url(image_url)
                domain = extract_domain(img_url) if img_url else None
                alt_text = self.safe_get_attribute(img,'alt')
                img_name = os.path.basename(img_url) if img_url else None

                # Include image data only if it is from the specified domain
                if domain == 'images.ctfassets.net':
                    images.append({
                        "image url": img_url,
                        "image name": img_name,
                        "alt text": alt_text if alt_text else "No Alt Text"
                    })
            return images
        except Exception as e:
            print(f"image found error {e}")


    def get_page_type(self):
        try:
            self.wait_for_page_load()
            locator = self.page.locator("head script")
            count = locator.count()
            cc_element = None

            for i in range(count):
                element = locator.nth(i)

                # Get the text content of the current script element
                sc_content = element.text_content()

                # Check if 'careClubConfig' is in the script content
                if "page_type" in sc_content:
                    cc_element = element
                    break

            if cc_element:
                script_content = cc_element.text_content()

                data_layer_main_str = script_content.split('window[\'dataLayer\'] = window[\'dataLayer\'] || [];')[1]
                data_layer_push = data_layer_main_str.split('window[\'dataLayer\'].push(')
                data_layer = None

                for i in range(len(data_layer_push)):
                    data_layer_str = data_layer_push[i].split(");")[0]
                    if "page_type" in data_layer_str:
                        data_layer = json.loads(data_layer_str)
                        break

                if data_layer:
                    page_data = data_layer.get("page_data", {})
                    page_type = page_data.get("page_type", None)
                    return page_type
                else:
                    print("\n\n Page_type not found\n\n")
                    return None
        except Exception as e:
            print(f"Error processing: {e}")