# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 15:11:59 2023

@author: LAPTOP
"""

import openai
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout

screen_helper = """
ScreenManager:
    WelcomeScreen:
    ChatScreen:

<WelcomeScreen>:
    name: 'welcome_screen'
    orientation: 'vertical'

    MDBoxLayout:
        adaptive_height: True
        orientation: 'vertical'
        spacing: '10dp'
        size_hint: .8, .4
        pos_hint: {"center_x": .5, "center_y": .6}      

        MDLabel:
            text: 'Welcome'
            valign: "center"
            halign: "center"

        MDTextField:
            id: name_field
            hint_text: "Enter your name to join the chat"
            mode: "rectangle" 
            pos_hint: {"center_x": .5}  

        MDRaisedButton:
            rounded_button: True
            padding: '10dp'
            text: "Join chat"
            on_press:
                root.manager.transition.direction = 'left'
                root.manager.current = 'chat_screen'
                app.join_chat()     
            pos_hint: {"center_x": .9} 

<ChatScreen>:
    name: 'chat_screen'
    orientation: 'vertical'
    MDBoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'  
                  

        MDBoxLayout:
            padding: '10dp'
            spacing: '10dp'
            adaptive_height: True            

            MDRectangleFlatButton:
                id: name_rect
                text: 'Your name'
                halign: 'center'
                valign: 'center'
                size_hint_x: .7

            MDRaisedButton:
                id: lang_button
                rounded_button: False
                pos_hint: {'center_x': .5, 'center_y': .5}
                size_hint_x: .3
                text: 'Language'
                halign: 'center'
                valign: 'center'
                on_release: root.drop()

        ScrollView:
            id: scroll_mes_hist
            do_scroll_x: False
            do_scroll_y: True
            Label:
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                padding: 10, 10
                id: chat_history
                font_name: 'NotoSans-Regular'
                markup: True


        MDBoxLayout:
            padding: '10dp'
            spacing: '10dp'
            adaptive_height: True

            MDTextField:
                id: message_input
                hint_text: "Type your message.."
                mode: "rectangle" 
                size_hint_x: .7
                height: "100dp"
                multiline: True
                max_height: "200dp"


            MDRaisedButton:
                rounded_button: False
                padding: '5dp'
                text: "Send"
                size_hint_x: .3
                on_release: 
                    app.send_message()
"""


class WelcomeScreen(Screen):
    pass

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = None
        Clock.schedule_once(self.on_kv_post)

    def on_kv_post(self, base_widget):
        lang_list = ['Armenian', 'English', 'Hindi', 'Konkani', 'Marathi', 'Poland',  'Slovene']
        menu_items = [{"text": f"{i}",
                       "viewclass": "OneLineListItem",
                       "height": dp(56),
                       "on_release": lambda x=f"{i}": self.menu_callback(x),

                       } for i in lang_list]

        self.dropdown = MDDropdownMenu(caller=self.ids.lang_button,
                                       header_cls=MenuHeader(),
                                       items=menu_items,
                                       width_mult=4,
                                       )

    def drop(self):
        self.dropdown.open()

    def menu_callback(self, text_item):
        app = MDApp.get_running_app()
        app.language = text_item
        self.ids.lang_button.text = text_item
        self.dropdown.dismiss()


class MenuHeader(MDBoxLayout):
    pass


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.title = "ChatApp"
        Config.set('kivy', 'window_title', 'ChatApp')

        key1 = 'sk-RZ3HcXfwixS98lmhlajJT3'
        key2 = 'BlbkFJE1AXtoTgkTG4UjpJQGdb'
        self.api_key = key1 + key2

        print(self.api_key)

        self.root = Builder.load_string(screen_helper)
        self.sm = ScreenManager()
        self.sm.add_widget(WelcomeScreen(name='welcome_screen'))
        self.sm.add_widget(ChatScreen(name='chat_screen'))

        return self.root

    def join_chat(self):
        app = MDApp.get_running_app()
        self.welcome_screen = app.root.get_screen('welcome_screen')
        self.chat_screen = app.root.get_screen('chat_screen')
        name = self.welcome_screen.ids.name_field.text

        if name == '':
            self.chat_screen.ids.name_rect.text = 'Anonimous'
        else:
            self.chat_screen.ids.name_rect.text = name

        self.language = 'English'

    def send_message(self):
        self.mes_text = self.chat_screen.ids.message_input.text
        self.chat_screen.ids.message_input.text = ''

        openai.api_key = self.api_key
        response_text = f"Translate the following text to {self.language}: {self.mes_text}"
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=[{"role": "user", "content": response_text},])
        translation = response['choices'][0]['message']['content']

        # response_text = f"Determine language: {self.mes_text}"
        # response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
        #                                         messages=[{"role": "user", "content": response_text}, ],
        #                                         )
        # input_language = response['choices'][0]['message']['content'][2:]
        input_language = 'english'
        if translation[:2] == '\n\n':
            translation = translation[2:]
        print(translation)

        if self.language.lower() == 'armenian':
            font_input = 'NotoSans-Regular'
            font_output = 'NotoSansArmenian'
        elif input_language.lower() == 'armenian':
            font_input = 'NotoSansArmenian'
            font_output = 'NotoSans-Regular'
        else:
            font_input = 'NotoSans-Regular'
            font_output = 'NotoSans-Regular'
        # self.chat_screen.ids.chat_history.add_widget(MDLabel(text=f"User: {self.mes_text}", font_name=font_input))
        # self.chat_screen.ids.chat_history.add_widget(MDLabel(text=f"Translation: {translation}", font_name=font_input))

        mes_text = f"[color=dd2020][font={font_input}]\nUser[/color] [color=20dddd]>:[/color] {self.mes_text}[/font]"
        translation_text = f"[color=dd2020][font={font_output}]\nTranslation[/color] [color=20dddd]>:[/color] {translation}[/font]" + "\n"

        self.chat_screen.ids.chat_history.text += mes_text
        self.chat_screen.ids.chat_history.text += translation_text

MainApp().run()


