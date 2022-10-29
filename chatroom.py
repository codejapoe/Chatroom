from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
import requests
from datetime import datetime

Window.clearcolor = (1, 1, 1, 1)
room = None
Builder.load_string('''
<Home>:
    BoxLayout:
        orientation: 'vertical'
        size: root.width, root.height

        Button:
            text: "Chatroom - Home"
            size_hint_y: 0.01
            valign: "top"
            background_color: 0, 1, 1
            disabled: True
            color: 0, 0.2, 0.8
            font_size: 22

        Label:
            id: warning
            text: ""
            size_hint: None, None
            size: self.texture_size 
            color: 1, 0, 0
            font_size: 18

        TextInput:
            id: nickname
            hint_text: "Nickname"
            size_hint_y: 0.1
            valign: "middle"
            focus: True
            multiline: False

        Button:
            text: "Enter"
            size_hint_y: 0.01
            background_color: 0, 1, 1
            on_press: root.enter()
            on_release:
                if warning.text == "": app.root.current = "lounge"
                root.manager.transition.direction = "left"

<Lounge>:
    BoxLayout:
        orientation: 'vertical'
        size: root.width, root.height

        Button:
            text: "Chatroom - Lounge"
            size_hint_y: 0.03
            valign: "top"
            background_color: 0, 1, 1, 1
            color: 1, 1, 1
            font_size: 22
            on_release:
                app.root.current = "home"
                root.manager.transition.direction = "right"

        Label:
            id: alert
            text: ""
            size_hint: None, None
            size: self.texture_size 
            color: 1, 0, 0
            font_size: 20

        Label:
            text: "Enter the code to join a room."
            size_hint: None, None
            size: self.texture_size 
            color: 0, 0, 1
            font_size: 18

        TextInput:
            id: join_code
            hint_text: "Code"
            size_hint_y: 0.1
            valign: "middle"
            focus: True
            multiline: False
            input_filter: 'int'

        Button:
            text: "Join Room"
            size_hint_y: 0.025
            background_color: 0, 1, 1
            on_press: root.join()
            on_release:
                if alert.text == "": app.root.current = "room"
                root.manager.transition.direction = "left"

        Label:
            text: "Enter the code to create a room."
            size_hint: None, None
            size: self.texture_size 
            color: 0, 0, 1
            font_size: 18

        TextInput:
            id: create_code
            hint_text: "Code"
            size_hint_y: 0.1
            valign: "middle"
            focus: True
            multiline: False
            input_filter: 'int'

        Button:
            text: "Create Room"
            size_hint_y: 0.025
            background_color: 0, 1, 1
            on_press: root.create()
            on_release:
                if alert.text == "": app.root.current = "room"
                root.manager.transition.direction = "left"

<Room>:
    BoxLayout:
        orientation: 'vertical'
        size: root.width, root.height

        Button:
            id: chat_code
            text: "Chatroom"
            size_hint_y: 0.13
            valign: "top"
            background_color: 0, 1, 1, 1
            color: 1, 1, 1
            font_size: 22
            on_press: root.leave()
            on_release:
                app.root.current = "lounge"
                root.manager.transition.direction = "right"

        TextInput:
            id: data
            hint_text: "Type any message here."
            size_hint_y: 0.1
            focus: True
            multiline: True

        Button:
            text: "Send Message"
            size_hint_y: 0.1
            background_color: 0, 1, 1
            on_press: root.send()

        ScrollView:
            Label:
                id: label
                text: ""
                size_hint: None, None
                size: self.texture_size 
                color: 0, 0.2, 0.8
''')

nickname = "User #Anonymous"

api = 'lhjujgh2W3BwvTUuKXqEv2rQLDqdUjgqed9OMVx6'

class Home(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.nickname.text = nickname
        pass

    def enter(self):
        global nickname
        nickname = self.ids.nickname.text
        
        if nickname == "":
            self.ids.warning.text = "Plase enter nickname."

        else:
            self.ids.warning.text = ""

class Lounge(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def join(self):
        code = self.ids.join_code.text
        
        if code == "":
            code = 0

        query = 'https://chat-room-native-default-rtdb.firebaseio.com/{}.json'.format(int(code))
        data = requests.get(query + '?auth=' + api).json()
        
        if data is None:
            self.ids.alert.text = "Room does not exist."

        else:
            global room
            self.ids.alert.text = ""
            room = int(code)
            
            time = datetime.now()
            now = time.strftime("%I:%M - %d-%b-%y")
            message = str(nickname + " joined this room.            (" + now + ")<linebreak>" + data['data'])
            requests.put(url = query + '?auth=' + api, json = {"data": message}).json()

    def create(self):
        code = self.ids.create_code.text
        
        if code == "":
            self.ids.alert.text = "Please enter the code."

        else:
            query = 'https://chat-room-native-default-rtdb.firebaseio.com/{}.json'.format(int(code))
            data = requests.get(query + '?auth=' + api).json()
            
            if data is not None:
                self.ids.alert.text = "The room already exists."

            else:
                global room
                self.ids.alert.text = ""
                room = int(code)

                url = 'https://chat-room-native-default-rtdb.firebaseio.com/{}.json'.format(room)
                time = datetime.now()
                now = time.strftime("%I:%M - %d-%b-%y")
                requests.put(url = url + '?auth=' + api, json = {"data": nickname + " created this room.            (" + now + ")"}).json()

class Room(Screen):    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.chat_code.text = "Chatroom: " + str(room)
        Clock.schedule_interval(self.update, 3)

    def update(self, *args):
        url = 'https://chat-room-native-default-rtdb.firebaseio.com/{}.json'.format(room)
        data = requests.get(url + '?auth=' + api).json()

        if data is None:
            text = "Loading...\nPlease be patient."
        
        else:
            text = data['data'].replace("<linebreak>", "\n")

        if room is None:
            self.ids.chat_code.text = "Chatroom"
        
        else:
            self.ids.chat_code.text = "Chatroom: " + str(room)
        
        self.ids.label.text = text

    def send(self):
        url = 'https://chat-room-native-default-rtdb.firebaseio.com/{}.json'.format(room)
        data = requests.get(url + '?auth=' + api).json()
        text = self.ids.data.text
        time = datetime.now()
        now = time.strftime("%I:%M - %d-%b-%y")
        text = nickname + " (" + now + ")" + ": " + text
        text = text.replace("\n", "<linebreak>")
        data = str(text + "<linebreak>" + data['data'])
        requests.put(url = url + '?auth=' + api, json = {"data": data}).json()

        self.ids.data.text = ""

    def leave(self):
        url = 'https://chat-room-native-default-rtdb.firebaseio.com/{}.json'.format(room)
        data = requests.get(url + '?auth=' + api).json()
        time = datetime.now()
        now = time.strftime("%I:%M - %d-%b-%y")
        
        message = str(nickname + " left this room.            (" + now + ")<linebreak>" + data['data'])
        requests.put(url = url + '?auth=' + api, json = {"data": message}).json()

        self.ids.data.text = ""

class Chatroom(App):
    def build(self):
        self.sm = ScreenManager()

        home = Home(name = "home")
        self.sm.add_widget(home)

        lounge = Lounge(name = "lounge")
        self.sm.add_widget(lounge)

        room = Room(name = "room")
        self.sm.add_widget(room)

        return self.sm

if __name__ == "__main__":
    Chatroom().run()