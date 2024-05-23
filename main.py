import tkinter as tk
import tkinter.font as tkFont
import pandas as pd

from tkinter import filedialog
from tkinter import ttk
from joblib import load

class App:
    global elems
    elems =  ['FeCr', 'FeMo', 'FeV'] # ['FeCr', 'FeMo', 'FeV', 'FeW', 'Ni']

    def __init__(self, root):
        self.root = root

        color = "#1F2541"
        ft = tkFont.Font(family='JetBrains Mono',size=14)
        ft2= tkFont.Font(family='JetBrains Mono',size=22)
        width, height = 700, 800
        # Какие-то настройки
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)

        # Поля для будущего
        self.file_path = None
        self.table = None
        self.scroll_pane = None
        self.models = {}

        # Какие-то настройки
        self.root.configure(bg=color)
        self.root.configure(cursor = "arrow")
        self.root.title("Построение модели")
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

        self.file_label = tk.Label(root,
                                   text="Добро пожаловать в приложение!",
                                   font=ft2,
                                   fg="#B4B4B4",
                                   bg="#1F2541",
                                   justify="center"
                                   )
        self.file_label.place(x=50, y=30, width=600, height=44)
        self.file_label = tk.Label(root,
                                   text="Расчет содержания веществ в сплаве:",
                                   font=ft2,
                                   fg="#B4B4B4",
                                   bg="#1F2541",
                                   justify="center"
                                   )
        self.file_label.place(x=5, y=80, width=700, height=44)

        # Создаем кнопку для загрузки файла
        self.load_button = tk.Button(root,
                                     text="Загрузить файл",
                                     command=self.load_file,
                                     bg="#B4B4B4",
                                     fg="#1F2541",
                                     font=ft,
                                     justify="center",
                                     relief = "flat",
                                     cursor="plus"


        )
        self.load_button.place(x=70, y=150, width=165, height=45)

        # Создаем метку для отображения имени выбранного файла
        self.file_label = tk.Label(root,
                                   text="",
                                   font=ft,
                                   fg="#1F2541",
                                   bg="#D1D0D0",
                                   justify="center"
        )
        self.file_label.place(x=250, y=150, width=380, height=44)

        # Создаем кнопку для расчета результата
        self.calculate_button = tk.Button(root,
                                     text="Рассчитать",
                                     command=self.calculate,
                                     bg="#B4B4B4",
                                     fg="#1F2541",
                                     font=ft,
                                     justify="center",
                                     relief="flat",



        )
        self.calculate_button.place(x=70,y=680,width=560,height=44)

        self.load_models()
        self.create_table()

    def calculate(self):
        if not self.file_path:
            tk.messagebox.showerror("Ошибка", "Файл не загружен")
            return

        if self.file_path.endswith(".csv"):
            df = pd.read_csv(self.file_path)
        else:
            df = pd.read_excel(self.file_path, engine='openpyxl')

        scrap_columns = [column for column in df.columns if 'Scrap_' in column]
        common_columns = ['TotalIngotsWeight', 'PouringScrap', 'OtherScrap']

        values = {} # 'HeatNo': df.HeatNo.to_list()
        for elem in elems:
            withot_Fe = f"{elem.replace('Fe', '')}"
            specific_columns = [f'{withot_Fe}_Last_EOP', f'{withot_Fe}_Final']
            predictors = df[sorted(common_columns + scrap_columns + specific_columns)].to_numpy()
            values[elem] = self.models[elem].predict(predictors)

        self.create_table(pd.DataFrame(values).astype('int').to_numpy())

    def load_models(self):
        try:
            for elem in elems:
                self.models[elem] = load(f'{elem}_model.joblib')
        except:
            tk.messagebox.showerror("Ошибка", f"Файл с моделью для {elem} не найден")
            return

    def create_table(self, values=[['' for _ in range(5)] for _ in range(18)]):
        """
        О создании таблицы https://www.youtube.com/watch?v=HMPIeZ3S_cs
        values - необязательный параметр. Если передается, то печатаем эти значения
        Если не передается, то делаем пустую таблицу из 18 строк (подобрано эмпирически)
        """
        if self.table:
            self.table.destroy()

        self.table = ttk.Treeview(self.root, show='headings')

        # Создание заголовка
        headers = elems # = ['HeatNo'] + elems
        self.table['columns'] = headers
        style = ttk.Style()
        style.configure('Treeview.Heading', bg = "#B4B4B4", font=('JetBrains Mono', 10, 'bold'))
        width_headers = { 'FeCr': 50, 'FeMo': 50, 'FeV': 50}
        for header in headers:
            self.table.heading(header, text=header, anchor='center')
            self.table.column(header, anchor='center', width=width_headers[header])
            self.table.tag_configure('Treeview.Heading', font=('JetBrains Mono', 10, 'bold'))

        # Вставка значений
        for row in values:
            self.table.insert('', tk.END, values=list(row))

        for _ in range(len(values), 18):
            self.table.insert('', tk.END, values=['' for __ in range(6)])

        # Настройка прокрутки
        self.scroll_pane = ttk.Scrollbar(self.root, command=self.table.yview)
        self.table.configure(yscrollcommand=self.scroll_pane.set)
        self.table.place(x=70, y=210, width=560, height=450)
        self.scroll_pane.place(x=70 + 544, y=212, height=447, width=15)


    def load_file(self):
        # Открываем диалоговое окно выбора файла
        file_path = filedialog.askopenfilename()

        # Проверяем тип файла
        if not (file_path.endswith(".csv") or file_path.endswith(".xlsx")):
            tk.messagebox.showerror("Ошибка", "Выбран неподдерживаемый тип файла")
            return

        # Сохраняем путь к выбранному файлу и отображаем его имя на метке
        self.file_path = file_path
        self.file_label.config(text=file_path.split("/")[-1])
        self.create_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
