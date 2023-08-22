import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
import os
import threading
import schedule
import time
import sqlite3

class PersonalAssistant:
    def __init__(self):
        self.user_authenticated = False
        self.db_connection = sqlite3.connect("user_accounts.db")
        self.create_table()
        

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                secret_phrase TEXT
            )
        ''')
        self.db_connection.commit()

    def create_account(self, username, password, secret_phrase):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, secret_phrase) VALUES (?, ?, ?)",
                           (username, password, secret_phrase))
            self.db_connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate(self, username, password, secret_phrase):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT password, secret_phrase FROM users WHERE username=?", (username,))
        row = cursor.fetchone()

        if row and row[0] == password and row[1] == secret_phrase:
            self.user_authenticated = True
            return True
        return False


    def set_reminder(self, message, interval):
        schedule.every(interval).seconds.do(self.send_notification, message)

    def send_notification(self, message):
        self.read_aloud(message)

    def read_aloud(self, text):
        tts = gTTS(text)
        tts.save("notification.mp3")
        os.system("start notification.mp3")  # Play the audio file (Windows)

    def start_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Assistant")
        self.assistant = PersonalAssistant()
        self.root.geometry("600x400")

        self.login_frame = tk.Frame(root)
        self.signup_frame = tk.Frame(root)
        self.main_frame = tk.Frame(root)

        self.create_login_ui()
        self.create_signup_ui()
        self.create_main_ui()

        self.show_login_ui()

    def create_login_ui(self):
        self.login_username_label = tk.Label(self.login_frame, text="Username:")
        self.login_username_label.pack()
        self.login_username_entry = tk.Entry(self.login_frame)
        self.login_username_entry.pack()

        self.login_password_label = tk.Label(self.login_frame, text="Password:")  # Add this line
        self.login_password_label.pack()  # Add this line
        self.login_password_entry = tk.Entry(self.login_frame, show="*")  # Add this line
        self.login_password_entry.pack()  # Add this line

        self.login_secret_label = tk.Label(self.login_frame, text="Secret Passphrase:")
        self.login_secret_label.pack()
        self.login_secret_entry = tk.Entry(self.login_frame, show="*")
        self.login_secret_entry.pack()

        self.login_button = tk.Button(self.login_frame, text="Log In", command=self.log_in)
        self.login_button.pack()

        self.create_account_button = tk.Button(self.login_frame, text="Create Account", command=self.show_signup_ui)
        self.create_account_button.pack()

    def create_signup_ui(self):
        self.signup_username_label = tk.Label(self.signup_frame, text="Username:")
        self.signup_username_label.pack()
        self.signup_username_entry = tk.Entry(self.signup_frame)
        self.signup_username_entry.pack()

        self.signup_password_label = tk.Label(self.signup_frame, text="Password:")
        self.signup_password_label.pack()
        self.signup_password_entry = tk.Entry(self.signup_frame, show="*")
        self.signup_password_entry.pack()


        self.signup_secret_label = tk.Label(self.signup_frame, text="Secret Passphrase:")
        self.signup_secret_label.pack()
        self.signup_secret_entry = tk.Entry(self.signup_frame, show="*")
        self.signup_secret_entry.pack()

        self.signup_button = tk.Button(self.signup_frame, text="Sign Up", command=self.sign_up)
        self.signup_button.pack()

    def create_main_ui(self):
        self.reminder_label = tk.Label(self.main_frame, text="Reminder:")
        self.reminder_label.pack()
        self.reminder_entry = tk.Entry(self.main_frame)
        self.reminder_entry.pack()

        self.interval_label = tk.Label(self.main_frame, text="Interval (seconds):")
        self.interval_label.pack()
        self.interval_entry = tk.Entry(self.main_frame)
        self.interval_entry.pack()

        self.set_reminder_button = tk.Button(self.main_frame, text="Set Reminder", command=self.set_reminder)
        self.set_reminder_button.pack()

        self.assistant_thread = threading.Thread(target=self.assistant.start_scheduler)
        self.assistant_thread.start()

    def show_login_ui(self):
        self.signup_frame.pack_forget()
        self.main_frame.pack_forget()
        self.login_frame.pack()

    def show_signup_ui(self):
        self.login_frame.pack_forget()
        self.main_frame.pack_forget()
        self.signup_frame.pack()

    def show_main_ui(self):
        self.login_frame.pack_forget()
        self.signup_frame.pack_forget()
        self.main_frame.pack()

    def log_in(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()
        secret_passphrase = self.login_secret_entry.get()

        if self.assistant.authenticate(username, password, secret_passphrase):
            messagebox.showinfo("Log In", "Authentication successful!")
            self.show_main_ui()
        else:
            messagebox.showerror("Log In", "Authentication failed.")


    def sign_up(self):
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()
        secret_passphrase = self.signup_secret_entry.get()

        if self.assistant.create_account(username, password, secret_passphrase):
            messagebox.showinfo("Sign Up", "Account created successfully!")
            self.show_login_ui()
        else:
            messagebox.showerror("Sign Up", "Username already exists.")

    def set_reminder(self):
        message = self.reminder_entry.get()
        interval = int(self.interval_entry.get())
        self.assistant.set_reminder(message, interval)
        messagebox.showinfo("Reminder", "Reminder set successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()
