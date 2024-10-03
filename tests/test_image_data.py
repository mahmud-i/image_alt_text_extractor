
import os
import pytest
import pandas as pd
from urllib.parse import urlparse
from utils.compare_image_data import image_compare
from utils.report_styling import DataFrameStyler


prod_data = []
stage_data = []
data_comparison = []
missing_image_alt_text = []


@staticmethod
def get_slug_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path.lstrip('/')


def test_images(open_prod_page, open_stage_page, url, prod_domain_url, stage_domain_url, type_of_test):
    try:
        slug = get_slug_from_url(url)
        stage_url = url.replace(prod_domain_url, stage_domain_url)

        def prod_image_data():
            prod_instance, page_type = open_prod_page
            if page_type in ['productListing', 'articleListing']:
                prod_instance.expand_list()
            prod_image = prod_instance.get_images_data()
            prod_instance.close_page()
            print(f"Prod image data: {prod_image}\n")
            for val in prod_image:
                row = {
                    'URL': url,
                    'Page Slug': slug,
                    'image url': val['image url'],
                    'image name': val['image name'],
                    'alt text': val['alt text']
                }
                prod_data.append(row)
            return prod_image

        def stage_image_data():
            stage_instance, page_type = open_stage_page
            if page_type in ['productListing', 'articleListing']:
                stage_instance.expand_list()
            stage_image = stage_instance.get_images_data()
            stage_instance.close_page()
            print(f"Stage image data: {stage_image}\n")
            for val in stage_image:
                row = {
                    'URL' : stage_url,
                    'Page Slug': slug,
                    'image url': val['image url'],
                    'image name': val['image name'],
                    'alt text': val['alt text']
                }
                stage_data.append(row)
            return stage_image

        def compare_image_data():
            image_data_compare = image_compare(prod_images,stage_images)
            print(f"Compare image data: \n{image_data_compare}\n")
            for val in image_data_compare:
                row = {
                        'URL' : url,
                        'Page Slug': slug,
                        'image url': val['image url'],
                        'image name': val['image name'],
                        'alt text in PROD': val['alt text in PROD'],
                        'alt text in Stage': val['alt text in Stage'],
                        'result': val['result']
                }
                data_comparison.append(row)

        def missing_image_data(images_data, urls):
            print('Images with missing alt text:\n')
            for img in images_data:
                if img['alt text'] == "No Alt Text":
                    print(f"Image Name: {img['image name']};  Image link: {img['image url']}\n")
                    row = {
                            'URL': urls,
                            'Page Slug': slug,
                            'image url': img['image url'],
                            'image name': img['image name']
                    }
                    missing_image_alt_text.append(row)

        prod_images = None
        stage_images = None

        if type_of_test == '1':
            prod_images = prod_image_data()
            missing_image_data(prod_images, url)
        elif type_of_test == '2':
            stage_images = stage_image_data()
            missing_image_data(stage_images, stage_url)
        elif type_of_test == '3':
            prod_images = prod_image_data()
            stage_images = stage_image_data()
            missing_image_data(prod_images, url)


        if prod_images:
            assert len(prod_images) > 0, f"No images found on {url}"
            for img in prod_images:
                assert img['alt text'] != "No Alt Text", f"Image {img['image name']} on {url} is missing alt text"

        if stage_images:
            assert len(stage_images) > 0, f"No images found on {stage_url}"
            for img in stage_images:
                assert img['alt text'] != "No Alt Text", f"Image {img['image name']} on {stage_url} is missing alt text"

    except Exception as e:
        print(f"Error processing {url}: {e}")



@pytest.fixture(scope='session', autouse=True)
def generate_report(brand_name, date_t, time_t):
    yield
    test_name = 'image_data'
    # After all tests run, generate the report
    df_prod_data = pd.DataFrame(prod_data)
    df_stage_data = pd.DataFrame(stage_data)
    df_data_comparison = pd.DataFrame(data_comparison)
    if missing_image_alt_text:
        df_missing_data = pd.DataFrame(missing_image_alt_text)
    else:
        df_missing_data = pd.DataFrame(columns=["URL", "Page Slug", "image url", "image name"])

    base_dc = f"Report/{brand_name}_Report/test_on_{date_t}/{time_t}/{brand_name}_{test_name}_Report"

    excel_report_dct = f"{base_dc}/{brand_name}_{test_name}_excel_Report"
    os.makedirs(excel_report_dct, exist_ok=True)
    print('Excel report generation start\n')
    with pd.ExcelWriter(f"{excel_report_dct}/{brand_name}_{test_name}_test_report.xlsx") as writer:
        if not df_data_comparison.empty:
            df_data_comparison.to_excel(writer, sheet_name=f"{test_name}_comparison", index=False)
        else:
            print(f"No comparison data for {test_name} is found. Skipping excel report generation.")
        if not df_prod_data.empty:
            df_prod_data.to_excel(writer, sheet_name=f"prod_{test_name}", index=False)
        else:
            print(f"No PROD data for {test_name} is found. Skipping excel report generation.")
        if not df_stage_data.empty:
            df_stage_data.to_excel(writer, sheet_name=f"stage_{test_name}", index=False)
        else:
            print(f"No Stage data for {test_name} is found. Skipping excel report generation.")
        if not df_missing_data.empty:
            df_missing_data.to_excel(writer, sheet_name='missing_image_alt_text', index=False)
        else:
            print(f"No missing data for {test_name} is found. Skipping excel report generation.")

    html_report_dc = f"{base_dc}/{brand_name}_{test_name}_html_general_Report"
    os.makedirs(html_report_dc, exist_ok=True)
    print('HTML report generation start\n')

    style_report_dct = f"{base_dc}/{brand_name}_{test_name}Style_HTML_Report"
    os.makedirs(style_report_dct, exist_ok=True)

    if not df_data_comparison.empty:
        df_data_comparison.to_html(f"{html_report_dc}/{brand_name}_{test_name}_comparison_Report.html", index=False)

        print('Comparison Data HTML report styling and update start\n')
        styler_comparison = DataFrameStyler(df_data_comparison)
        styler_comparison.apply_styling_report()
        styler_comparison.generate_style_report(f"{style_report_dct}/{brand_name}_{test_name}_comparison_Report.html")

    if not df_prod_data.empty:
        df_prod_data.to_html(f"{html_report_dc}/{brand_name}_prod_{test_name}_Report.html", index=False)

        print('PROD Data HTML report styling and update start\n')
        styler_production = DataFrameStyler(df_prod_data)
        styler_production.apply_styling_report()
        styler_production.generate_style_report(f"{style_report_dct}/{brand_name}_prod_{test_name}_Report.html")

    if not df_stage_data.empty:
        df_stage_data.to_html(f"{html_report_dc}/{brand_name}_stage_{test_name}_Report.html", index=False)

        print('Stage Data HTML report styling and update start\n')
        styler_stage = DataFrameStyler(df_stage_data)
        styler_stage.apply_styling_report()
        styler_stage.generate_style_report(f"{style_report_dct}/{brand_name}_stage_{test_name}_Report.html")

    if not df_missing_data.empty:
        df_missing_data.to_html(f"{html_report_dc}/{brand_name}_missing_image_alt_text_Report.html", index=False)

        print('Missing Alt text Data HTML report styling and update start\n')
        styler_missing = DataFrameStyler(df_missing_data)
        styler_missing.apply_styling_report()
        styler_missing.generate_style_report(f"{style_report_dct}/{brand_name}_missing_image_alt_text_Report.html")
    else:
        print("No missing image alt text data found. Skipping HTML report generation.")

    print(f"All data checking and Report creation is done for {brand_name}_{test_name}_at_{base_dc}.\n\n")