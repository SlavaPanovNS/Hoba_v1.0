from tkinter import *
import tkinter.filedialog
import exifread
from datetime import datetime
import os
import shutil


class GUIHoba(): # Графический интерфейс tkinter

    def __init__(self):
        self.engine = EngineHoba()
        self.window = Tk()
        self.window.title("Hoba! v1.0 (Сортировщик фотографий)")
        # Поместить приложение в центр экрана и сделать его размер всегда пропорциональным разрешению экана
        self.window.geometry(f'{int(self.window.winfo_screenwidth()/3)}x{int(self.window.winfo_screenheight()/2)}+'
                        f'{int(self.window.winfo_screenwidth()/2) - int(self.window.winfo_screenwidth()/6)}+'
                        f'{int(self.window.winfo_screenheight()/2) - int(self.window.winfo_screenheight()/4)}')

        self.l1 = Label(text="Hoba!", font=("Arial Bold", 30), width=30, height=5)

        self.l2 = Label(self.window, text="Данная утилита предназначена для сортировки фотографий.\n"
                                "Она создает папки с годами, а в них папки с месяцами.\n"
                                "Внутри каждого месяца помещаются ваши фотографии.", font=("Arial", 12))

        self.btn = Button(self.window, text="Выбрать папку для сортировки", command=self.get_path_to_fotoflder)

        self.l3 = Label(self.window)
        self.l4 = Frame(self.window)
        self.btn2 = Button(self.l4, text="Начать", command=self.start)
        self.btn3 = Button(self.l4, text="Отмена", command=self.cancel)

        self.l1.pack()
        self.l2.pack()
        self.btn.pack()
        self.l3.pack()
        self.l4.pack()
        self.btn2.pack(side=LEFT)
        self.btn3.pack(side=RIGHT)
        self.btn2.config(state='disabled')
        self.btn3.config(state='disabled')

        self.window.mainloop()

    # Кнопка Выбрать папку для сортировки
    def get_path_to_fotoflder(self):
        self.path_to_fotoflder = tkinter.filedialog.askdirectory()
        self.engine.get_path_to_fotofolder(self.path_to_fotoflder)
        self.get_but(self.path_to_fotoflder)

    #  Функция активации кнопок после выбора папки
    def get_but(self, dir_name):
        self.dir_name = dir_name
        self.l3.configure(text=dir_name)
        self.btn2.config(state='normal')
        self.btn3.config(state='normal')

    #  Кнопка Отмена
    def cancel(self):
        self.l3.configure(text='')
        self.btn2.config(state='disabled')
        self.btn3.config(state='disabled')

    # Копка Начать
    def start(self):
        self.other_files = self.engine.sort()
        self.done(self.other_files)

    # Функция показывающая результаты после завершения сортировки
    def done(self, other):
        self.other = other
        self.btn2.config(state='disabled')
        self.btn3.config(state='disabled')
        if self.other == None:
            self.l3.configure(text="Готово!")
        else:
            self.l3.configure(text="Готово!\n"
                              "Есть неотсортированные файлы!\n"
                              f"{[i for i in self.other]}")

class EngineHoba(): # Движок

    def __init__(self):
        # Словарь с месяцами
        self.monthdct = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь',
                    7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
        # Список форматов
        self.image_format = ['.jpg', '.HEIC', '.JPG', '.png', '.jpeg']


    def get_path_to_fotofolder(self, path):
        self.path_to_fotoflder = path

    def sort (self):
        os.chdir(self.path_to_fotoflder)

        # Получить список файлов в папке
        self.file_list = os.listdir('.')

        # Обойти все файлы в папке и получить список путей только к фото
        self.path_to_foto_list = []
        self.other_files = []
        for i in self.file_list:
            name = os.path.splitext(i)[1]
            if name in self.image_format:
                self.path_to_foto_list.append(os.path.abspath(i))
            else:
                if i == '.DS_Store':
                    pass
                else:
                    self.other_files.append(i)

        # Создать необходмые директории для каждого года и месяца
        for i in self.path_to_foto_list:
            self.datee = self.get_date(i)
            self.path_to = self.make_dir_for_foto(self.path_to_fotoflder, self.datee)
            if not self.check_dup(i, self.path_to):
                self.move_to_new_dir(i, self.path_to)
            else:
                self.move_to_other_dir(self.path_to_fotoflder, i)
        return self.other_files

    # Функция считывания даты на фото
    def get_date(self, path_to_image):
        self.path_to_image = path_to_image
        self.name = os.path.splitext(self.path_to_image)[1]
        if self.name not in ['.HEIC']:

            # Перевести дату из формата IfdTag в формат строки
            with open(self.path_to_image, 'rb') as fh:
                self.tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
                if "EXIF DateTimeOriginal" in self.tags:
                    self.dateTaken = str(self.tags["EXIF DateTimeOriginal"])

                    # Перевести строку в datetime
                    self.datee = datetime.strptime(self.dateTaken, "%Y:%m:%d %H:%M:%S")
                else:
                    self.datee = self.modification_date(self.path_to_image)
        else:
            self.datee = self.modification_date(self.path_to_image)

        return self.datee

    # Функция считывания даты с файла
    def modification_date(self, path_to_image):
        self.path_to_image = path_to_image
        self.t = os.path.getmtime(self.path_to_image)
        return datetime.fromtimestamp(self.t)

    # Функция создания необходимой папки для каждого года и месяца
    def make_dir_for_foto(self, path, datee):
        self.path = path
        self.datee = datee
        #  Переходим в нужную папку
        os.chdir(self.path)

        #  Проверяем наличие папки года и при отсутствии добавляем ее
        if not os.path.exists(f'{self.datee.year}'):
            os.mkdir(f'{self.datee.year}')

        #  Переходим в папку года
        os.chdir(f'{self.datee.year}')

        #  Проверяем наличие папки месяца и при отсутствии добавляем ее
        if not os.path.exists(f'{self.monthdct[self.datee.month]}'):
            os.mkdir(f'{self.monthdct[self.datee.month]}')
        os.chdir(f'{self.monthdct[self.datee.month]}')
        return os.getcwd()

    # Функция перемещения фото в нужную папку
    def move_to_new_dir(self, foto, path_to):
        self.foto = foto
        self.path_to = path_to
        # Проверка на то что foto является файлом
        if os.path.isfile(self.foto):
            shutil.move(self.foto, self.path_to)

    # Функция перемещения в папку Повторки
    def move_to_other_dir(self, path, foto):
        self.foto = foto
        self.path = path
        os.chdir(self.path)
        if not os.path.exists(f'Повторки'):
            os.mkdir(f'Повторки')
        os.chdir(f'Повторки')
        if os.path.isfile(self.foto):
            shutil.move(self.foto, os.getcwd())

    # Функция проверки наличия дубликата фото в папке назначения
    def check_dup(self, foto, path_to):
        self.foto = foto
        self.path_to = path_to
        if os.path.exists(os.path.join(self.path_to, os.path.split(self.foto)[1])):
            return True


if __name__ == "__main__":
    hoba = GUIHoba()