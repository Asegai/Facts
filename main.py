import requests
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
import json
from datetime import date
import os

def get_api_key():
    try:
        with open('api_key.json', 'r') as file:
            data = json.load(file)
            return data.get('api_key', '').strip()
    except FileNotFoundError:
        return ''

class ImageButton(ButtonBehavior, Image):
    pass

class FunFactApp(App):
    def build(self):
        root_layout = FloatLayout()

        center_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(200, 50), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.button = Button(text="Get Fun Fact!", size_hint=(None, None), size=(200, 50), font_size='20sp')
        self.button.bind(on_press=self.fetch_and_display_fact)
        center_layout.add_widget(self.button)
        root_layout.add_widget(center_layout)

        self.fact_label = Label(text="", font_size='20sp', halign='center', valign='top', size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.5}, text_size=(400, None), size_hint_y=None)
        root_layout.add_widget(self.fact_label)

        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        close_button = ImageButton(source=os.path.join(BASE_PATH, 'close_button_icon.png'), size_hint=(None, None), size=(50, 50), pos_hint={'right': 1, 'top': 1})
        close_button.bind(on_press=self.stop)
        root_layout.add_widget(close_button)

        history_button = ImageButton(source=os.path.join(BASE_PATH, 'history_icon.png'), size_hint=(None, None), size=(50, 50), pos_hint={'x': 0, 'top': 1})
        history_button.bind(on_press=self.show_history)
        root_layout.add_widget(history_button)

        key_button = Button(text="API Key", size_hint=(None, None), size=(100, 50), pos_hint={'x': 0, 'y': 0})
        key_button.bind(on_press=self.show_key_popup)
        root_layout.add_widget(key_button)

        if self.check_fun_fact_fetched_today():
            self.set_button_disabled()
            self.fact_label.text = "Sorry! You've already seen today's fun fact."
            self.display_saved_fun_fact()

        return root_layout

    def fetch_and_display_fact(self, *args):
        api_url = 'https://api.api-ninjas.com/v1/facts?'
        my_api_key = get_api_key()
        if not my_api_key:
            error_popup = Popup(title='Error', content=Label(text="API key is missing. Please set the API key using the 'Key' button."), size_hint=(0.8, 0.4))
            error_popup.open()
            return
        headers = {'X-Api-Key': my_api_key}
        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code == requests.codes.ok:
                fact = response.json()[0]['fact']
                self.fact_label.text = fact + "\n\nThat's today's fun fact, come back tomorrow for more!"
                self.set_button_disabled()
                self.record_fun_fact_fetched_today(fact)
            else:
                error_popup = Popup(title='Error', content=Label(text=f"Error: {response.status_code}\n{response.text}"), size_hint=(0.8, 0.4))
                error_popup.open()
        except requests.exceptions.RequestException as e:
            error_popup = Popup(title='Error', content=Label(text=f"Failed to fetch fun fact \nPlease check your internet connection or API key validity."), size_hint=(0.8, 0.4))
            error_popup.open()

    def set_button_disabled(self):
        self.button.disabled = True
        self.button.opacity = 0

    def check_fun_fact_fetched_today(self):
        today = date.today().isoformat()
        try:
            with open('today_fact.json', 'r') as file:
                data = json.load(file)
                return data.get(today, False)
        except FileNotFoundError:
            return False

    def record_fun_fact_fetched_today(self, fact):
        today = date.today().isoformat()
        try:
            with open('today_fact.json', 'r+') as file:
                data = json.load(file)
                data[today] = {
                    'fact': fact
                }
                file.seek(0)
                json.dump(data, file, indent=4)
        except FileNotFoundError:
            with open('today_fact.json', 'w') as file:
                data = {today: {'fact': fact}}
                json.dump(data, file, indent=4)

    def display_saved_fun_fact(self):
        today = date.today().isoformat()
        try:
            with open('today_fact.json', 'r') as file:
                data = json.load(file)
                fact = data[today]['fact']
                self.fact_label.text = fact + "\n\nThat's today's fun fact, come back tomorrow for more!"
        except FileNotFoundError:
            pass
        except KeyError:
            pass

    def show_history(self, *args):
        try:
            with open('today_fact.json', 'r') as file:
                data = json.load(file)
                facts = "\n".join(f"{date}: {details['fact']}" for date, details in data.items())
                history_content = Label(text=facts, text_size=(400, None), valign='top', halign='left')
                history_popup = Popup(title='History', content=history_content, size_hint=(0.8, 0.8))
                history_popup.open()
        except FileNotFoundError:
            error_popup = Popup(title='Error', content=Label(text="No history found."), size_hint=(0.8, 0.4))
            error_popup.open()

    def show_key_popup(self, *args):
        key_popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        key_popup_label = Label(text="Enter API Key:", size_hint=(None, None), size=(200, 50))
        self.key_popup_textinput = TextInput(size_hint=(None, None), size=(400, 50), multiline=False)
        key_popup_submit = Button(text="Submit", size_hint=(None, None), size=(200, 50))
        key_popup_submit.bind(on_press=self.save_api_key)
        key_popup_layout.add_widget(key_popup_label)
        key_popup_layout.add_widget(self.key_popup_textinput)
        key_popup_layout.add_widget(key_popup_submit)
        self.key_popup = Popup(title='API Key', content=key_popup_layout, size_hint=(0.8, 0.4))
        self.key_popup.open()

    def save_api_key(self, *args):
        api_key = self.key_popup_textinput.text.strip()
        if api_key:
            with open('api_key.json', 'w') as file:
                json.dump({'api_key': api_key}, file)
            self.key_popup.dismiss()
        else:
            error_popup = Popup(title='Error', content=Label(text="API key cannot be empty."), size_hint=(0.8, 0.4))
            error_popup.open()

if __name__ == '__main__':
    FunFactApp().run()
