
def image_compare(data_to_check, data_ref):
    compare_data = []
    for image_1 in data_to_check:
        url_1 = image_1['image url']
        name_1 = image_1['image name']
        alt_text_1 = image_1['alt text']
        name_2 = None
        alt_text_2 = None
        for image_2 in data_ref:
            if image_2['image url'] == url_1 :
                name_2 = image_2['image name']
                alt_text_2 = image_2['alt text']
                break

        if name_2 is None :
            result = 'Not found image with same name in stage'
        elif alt_text_1 == 'No Alt Text' and alt_text_2 == 'No Alt Text':
            result = 'Both Null'
        elif alt_text_1 == 'No Alt Text':
            result = 'Missing in Prod'
        elif alt_text_1 != alt_text_2:
            result = 'Not Matched'
        else:
            result = 'Match'

        compare_data.append({
            "image url": image_1['image url'],
            "image name": name_1,
            "alt text in PROD": alt_text_1,
            "alt text in Stage": alt_text_2,
            "result": result
        })

    return compare_data