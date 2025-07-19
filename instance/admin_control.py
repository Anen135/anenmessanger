import sqlite3
import os

# Подключение к базе данных user.db
conn = sqlite3.connect('instance/users.db')
cursor = conn.cursor()

print("Введите SQL-запрос (Ctrl+C для выхода):")

try:
    while True:
        # Чтение команды от пользователя
        command = input('SQL> ')

        try:
            # Выполнение команды
            cursor.execute(command)

            # Если запрос возвращает данные (например, SELECT)
            if command.strip().lower().startswith('select'):
                results = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                for row in results:
                    for col_name, col_value in zip(column_names, row):
                        print(f"{col_name}: {col_value}")
            else:
                # Для команд изменения данных (INSERT, UPDATE, DELETE)
                conn.commit()
                print("Запрос выполнен успешно.")

        except sqlite3.Error as e:
            os.system(command)

except KeyboardInterrupt:
    print("\nВыход из программы.")
finally:
    # Закрытие соединения с базой данных
    conn.close()
