import sys

import ijson


def main(path):
    checked = []
    extracted = 0
    repeated = {}

    with open(path, "rb") as f:
        for item in ijson.items(f, "item"):
            extracted += 1
            str_l = str(item)
            if str_l not in checked:
                checked.append(str_l)
            else:
                _id = item["ration_card_details"]["राशनकार्ड संख्या"]
                repeated[_id] = repeated.get(_id, 0) + 1
                # print(l['url'])

    print("Times repeated:")
    print(repeated.values())
    print(f"Unique values: {len(checked)}")
    print(f"Extracted values: {extracted}")


if __name__ == "__main__":
    try:
        path = sys.argv[1]
        main(path)
    except Exception as e:
        print(f"Path error: {e}")
