import requests
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup

def get_api_key():
    with open('api_key.py', 'r') as file:
        return file.read().strip()

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

        return root_layout

    def fetch_and_display_fact(self, *args):
        api_url = 'https://api.api-ninjas.com/v1/facts?'
        my_api_key = get_api_key()
        headers = {'X-Api-Key': my_api_key}
        response = requests.get(api_url, headers=headers)

        if response.status_code == requests.codes.ok:
            fact = response.json()[0]['fact']
            self.fact_label.text = fact + "\n\nThat's today's fun fact, come back tomorrow for more!"
            self.button.disabled = True  
            self.button.opacity = 0  
        else:
            error_popup = Popup(title='Error', content=Label(text=f"Error: {response.status_code}\n{response.text}"), size_hint=(0.8, 0.4))
            error_popup.open()

if __name__ == '__main__':
    FunFactApp().run()
  
