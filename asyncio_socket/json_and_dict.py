import json


def json2dict(json_path: str):
    try:
        with open(json_path, "r", encoding="UTF-8") as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = {}
            return data
    except FileNotFoundError:
        print('File Not Found')
        return {}


def dict2json(json_path: str, source_dict: dict):
    with open(json_path, "w", encoding="UTF-8") as file:
        data = json.dumps(source_dict, ensure_ascii=False, indent=4, sort_keys=True).encode("UTF-8")
        file.write(data.decode())
