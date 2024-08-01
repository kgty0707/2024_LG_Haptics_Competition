def search_by(Palette_num):
    file_path = f"./{Palette_num}.txt"

    with open(file_path, 'r', encoding='utf-8') as file:
        info = file.read()

    return info