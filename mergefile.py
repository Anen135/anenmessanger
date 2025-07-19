import os

def merge_files(input_folder, output_file):
    """
    Читает все файлы из папки и объединяет их в один файл с разделителями,
    сохраняя оригинальные переносы строк.
    
    :param input_folder: Путь к папке с файлами
    :param output_file: Путь к выходному файлу
    """
    with open(output_file, 'wb') as outfile:  # Открываем в бинарном режиме
        for filename in os.listdir(input_folder):
            filepath = os.path.join(input_folder, filename)
            
            # Пропускаем подпапки и сам выходной файл, если он есть в папке
            if os.path.isdir(filepath) or filename == os.path.basename(output_file):
                continue
                
            try:
                # Записываем разделитель с именем файла (добавляем только один \n в конце)
                separator = f"\n%%============={filename}========%%\n".encode('utf-8')
                outfile.write(separator)
                
                # Читаем файл в бинарном режиме и записываем как есть
                with open(filepath, 'rb') as infile:
                    outfile.write(infile.read())
                    
            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {str(e)}")
                continue

if __name__ == "__main__":
    input_folder = "./"
    output_file = "./main.txt"
    
    if not os.path.isdir(input_folder):
        print("Ошибка: указанная папка не существует!")
    else:
        merge_files(input_folder, output_file)
        print(f"Все файлы из папки '{input_folder}' успешно объединены в '{output_file}'")