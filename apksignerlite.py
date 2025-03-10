import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style, Frame, Button, Checkbutton, Label, Text, Scrollbar
from ttkbootstrap.constants import *

class APKSignerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("APK Signer Lite")
        self.root.geometry("800x600")
        
        # Инициализация стилей Material Design
        self.style = Style(theme="cosmo")
        
        # Основной фрейм
        self.main_frame = Frame(self.root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Переменные для чекбоксов
        self.v1_var = tk.BooleanVar(value=True)
        self.v2_var = tk.BooleanVar(value=True)
        self.v3_var = tk.BooleanVar(value=True)
        self.v4_var = tk.BooleanVar(value=False)
        
        # Переменные для путей
        self.apk_files = []
        self.key_file = os.path.join(os.path.dirname(__file__), "tools", "testkey.pk8")
        self.cert_file = os.path.join(os.path.dirname(__file__), "tools", "testkey.x509.pem")
        self.apksigner_path = os.path.join(os.path.dirname(__file__), "tools", "apksigner.jar")
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Заголовок
        Label(self.main_frame, text="APK Signer Lite", font=("Helvetica", 18, "bold")).pack(pady=10)
        
        # Кнопка выбора APK
        self.apk_button = Button(self.main_frame, text="Выбрать APK(s)", command=self.select_apks, bootstyle=PRIMARY)
        self.apk_button.pack(pady=5)
        
        # Метка для выбранных APK
        self.apk_label = Label(self.main_frame, text="Выбрано APK: 0", bootstyle=INFO)
        self.apk_label.pack(pady=5)
        
        # Фрейм для чекбоксов версий подписи
        sig_frame = Frame(self.main_frame)
        sig_frame.pack(pady=10)
        
        Label(sig_frame, text="Версии подписи:", font=("Helvetica", 12)).grid(row=0, column=0, columnspan=4, pady=5)
        Checkbutton(sig_frame, text="v1", variable=self.v1_var, bootstyle="success").grid(row=1, column=0, padx=5)
        Checkbutton(sig_frame, text="v2", variable=self.v2_var, bootstyle="success").grid(row=1, column=1, padx=5)
        Checkbutton(sig_frame, text="v3", variable=self.v3_var, bootstyle="success").grid(row=1, column=2, padx=5)
        Checkbutton(sig_frame, text="v4", variable=self.v4_var, bootstyle="success").grid(row=1, column=3, padx=5)
        
        # Кнопка выбора ключей
        self.key_button = Button(self.main_frame, text="Выбрать ключ и сертификат", command=self.select_keys, bootstyle=SECONDARY)
        self.key_button.pack(pady=5)
        
        # Метка для ключей
        self.key_label = Label(self.main_frame, text=f"Ключ: {os.path.basename(self.key_file)}\nСертификат: {os.path.basename(self.cert_file)}", bootstyle=INFO)
        self.key_label.pack(pady=5)
        
        # Кнопка проверки подписи
        self.verify_button = Button(self.main_frame, text="Проверить подпись", command=self.verify_apks, bootstyle=WARNING)
        self.verify_button.pack(pady=5)
        
        # Кнопка подписи
        self.sign_button = Button(self.main_frame, text="Подписать APK", command=self.sign_apks, bootstyle=SUCCESS)
        self.sign_button.pack(pady=10)
        
        # Окно логов
        Label(self.main_frame, text="Логи:", font=("Helvetica", 12)).pack(pady=5)
        self.log_text = Text(self.main_frame, height=10, width=80)
        self.log_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Скроллбар для логов
        scrollbar = Scrollbar(self.main_frame, command=self.log_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
    def select_apks(self):
        files = filedialog.askopenfilenames(
            title="Выберите APK-файлы",
            filetypes=[("APK files", "*.apk")]
        )
        if files:
            self.apk_files = list(files)
            self.apk_label.config(text=f"Выбрано APK: {len(self.apk_files)}")
            self.log(f"Выбрано файлов: {len(self.apk_files)}")
            for file in self.apk_files:
                self.log(f" - {file}")
    
    def select_keys(self):
        key_file = filedialog.askopenfilename(
            title="Выберите файл ключа (.pk8)",
            filetypes=[("PK8 files", "*.pk8")]
        )
        if key_file:
            self.key_file = key_file
            cert_file = filedialog.askopenfilename(
                title="Выберите файл сертификата (.pem)",
                filetypes=[("PEM files", "*.x509.pem")]
            )
            if cert_file:
                self.cert_file = cert_file
                self.key_label.config(text=f"Ключ: {os.path.basename(self.key_file)}\nСертификат: {os.path.basename(self.cert_file)}")
                self.log(f"Выбран ключ: {self.key_file}")
                self.log(f"Выбран сертификат: {self.cert_file}")

    def verify_apks(self):
        if not self.apk_files:
            messagebox.showerror("Ошибка", "Выберите хотя бы один APK-файл!")
            return
        
        if not os.path.exists(self.apksigner_path):
            messagebox.showerror("Ошибка", f"Файл {self.apksigner_path} не найден!")
            return
        
        self.log("Проверка подписи APK...")
        
        for apk in self.apk_files:
            cmd = ["java", "-jar", self.apksigner_path, "verify", "--verbose", apk]
            self.log(f"Команда проверки: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"Информация о подписи {os.path.basename(apk)}:")
                    self.log(result.stdout)
                else:
                    self.log(f"Ошибка проверки {apk}:")
                    self.log(result.stderr)
            except Exception as e:
                self.log(f"Исключение при проверке {apk}: {str(e)}")

    def sign_apks(self):
        if not self.apk_files:
            messagebox.showerror("Ошибка", "Выберите хотя бы один APK-файл!")
            return
        
        if not os.path.exists(self.apksigner_path):
            messagebox.showerror("Ошибка", f"Файл {self.apksigner_path} не найден!")
            return
        
        # Формирование команд для подписи с явным указанием v4
        base_cmd = [
        "java", "-jar", self.apksigner_path, "sign",
        "--key", self.key_file,
        "--cert", self.cert_file
        ]
        
        # Формирование команд для подписи
        sig_options = []
        if self.v1_var.get(): sig_options.append("--v1-signing-enabled=true")
        else: sig_options.append("--v1-signing-enabled=false")
        if self.v2_var.get(): sig_options.append("--v2-signing-enabled=true")
        else: sig_options.append("--v2-signing-enabled=false")
        if self.v3_var.get(): sig_options.append("--v3-signing-enabled=true")
        else: sig_options.append("--v3-signing-enabled=false")
        if self.v4_var.get(): sig_options.append("--v4-signing-enabled=true")
        else: sig_options.append("--v4-signing-enabled=false")
        
        self.log("Начинается процесс подписи...")
        
        for apk in self.apk_files:
            output_apk = apk.replace(".apk", "_signed.apk")
            full_cmd = base_cmd + sig_options + ["--out", output_apk, apk]
            
            self.log(f"Команда: {' '.join(full_cmd)}")
            
            try:
                result = subprocess.run(full_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log(f"Успешно подписан: {output_apk}")
                    if self.v4_var.get():
                       verify_cmd = ["java", "-jar", self.apksigner_path, "verify", "--verbose", output_apk]
                       verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
                       if verify_result.returncode == 0:
                           self.log(f"Подтверждена подпись v4 для {output_apk}")
                       else:
                        self.log(f"Предупреждение: Проблемы с подписью v4 для {output_apk}")
                else:
                    self.log(f"Ошибка при подписи {apk}:")
                    self.log(result.stderr)
            except Exception as e:
                self.log(f"Исключение при подписи {apk}: {str(e)}")
        
        messagebox.showinfo("Готово", "Процесс подписи завершен. Проверьте логи.")
    
    def log(self, message):
        self.log_text.insert(END, f"{message}\n")
        self.log_text.see(END)

if __name__ == "__main__":
    root = tk.Tk()
    app = APKSignerApp(root)
    root.mainloop()