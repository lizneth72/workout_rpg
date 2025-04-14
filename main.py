from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.audio import SoundLoader  # Add this import
from kivy.animation import Animation
from datetime import datetime
import json
import os
import random

# Set portrait orientation
#Window.size = (480, 800)

class WorkoutRPG(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=20, **kwargs)

        # Load the level-up sound
        self.level_up_sound = SoundLoader.load('level_up_sound.mp3')  # Make sure this file exists

        self.stats = {
            'level': 1,
            'exp': 0,
            'hp': 100,
            'max_hp': 100,
            'strength': 0,
            'stamina': 0,
            'agility': 0,
            'last_login': str(datetime.now().date()),
            'total_reps': 0,
            'event_cooldown_triggered': False,
            'quests': [],
            'daily_quests': [],
            'quests_completed': 0
        }
        self.exp_to_level = 100
        self.event_cooldown = 40
        self.boss_active = False
        self.boss_hp = 0
        self.save_file = 'rpg_save.json'
        self.load_progress()

        self.stats.setdefault('daily_quests', [])
        self.stats.setdefault('quests_completed', 0)
        self.stats.setdefault('event_cooldown_triggered', False)
        self.stats.setdefault('quests', [
            {"task": "Do 20 push-ups", "progress": 0, "goal": 20, "type": "push-ups"},
            {"task": "Run 15 times", "progress": 0, "goal": 15, "type": "running"},
            {"task": "Air Bike 10 reps", "progress": 0, "goal": 10, "type": "air bike"}
        ])

        self.apply_daily_decay()

        self.status_label = Label(text=self.get_status_text(), font_size=28, size_hint=(1, 0.3), bold=True, color=(0.2, 0.2, 0.2, 1))
        self.hp_bar = ProgressBar(max=self.stats['max_hp'], value=self.stats['hp'], size_hint=(1, 0.07))
        self.hp_label = Label(text=f"HP: {self.stats['hp']}/{self.stats['max_hp']}", size_hint=(1, 0.07), font_size=20)
        self.exp_bar = ProgressBar(max=self.exp_to_level, value=self.stats['exp'], size_hint=(1, 0.07))
        self.exp_label = Label(text=f"EXP: {self.stats['exp']}/{self.exp_to_level}", size_hint=(1, 0.07), font_size=20)

        self.add_widget(self.status_label)
        self.add_widget(self.hp_bar)
        self.add_widget(self.hp_label)
        self.add_widget(self.exp_bar)
        self.add_widget(self.exp_label)

        for quest in self.stats['quests']:
            self.add_widget(Label(text=f"Quest: {quest['task']} ({quest['progress']}/{quest['goal']})", font_size=20))

        self.add_widget(Label(text="Daily Quests:", font_size=22))
        self.daily_quest_labels = []
        for quest in self.stats['daily_quests']:
            quest_label = Label(text=f"{quest['task']} ({quest['progress']}/{quest['goal']})", font_size=18)
            self.daily_quest_labels.append(quest_label)
            self.add_widget(quest_label)

        self.add_workout_button("Push-ups", 'strength')
        self.add_workout_button("Running", 'stamina')
        self.add_workout_button("Air Bike", 'agility')
        self.add_workout_button("Sit-ups", 'stamina')

        save_button = Button(text="Save Game", size_hint=(1, 0.12), font_size=24, background_color=(0.2, 0.6, 0.2, 1))
        save_button.bind(on_press=self.save_progress)
        self.add_widget(save_button)

    def add_workout_button(self, label, stat):
        btn = Button(text=label, size_hint=(1, 0.12), font_size=24, background_color=(0.1, 0.4, 0.8, 1))
        btn.bind(on_press=lambda x: self.animate_button(btn, stat, label.lower()))
        self.add_widget(btn)

    def animate_button(self, button, stat, label):
        anim = Animation(size_hint=(1, 0.14), duration=0.1) + Animation(size_hint=(1, 0.12), duration=0.1)
        anim.start(button)
        self.handle_workout(stat, label)

    def handle_workout(self, stat, label):
        self.stats[stat] += 1
        self.stats['exp'] += 1
        self.stats['total_reps'] += 1

        for quest in self.stats['quests']:
            if quest.get('type') in label:
                quest['progress'] = min(quest['progress'] + 1, quest['goal'])

        for quest in self.stats['daily_quests']:
            if quest.get('type') in label:
                quest['progress'] = min(quest['progress'] + 1, quest['goal'])

        if self.stats['exp'] >= self.exp_to_level:
            self.stats['level'] += 1
            self.stats['exp'] = 0
            self.stats['max_hp'] += 1
            self.stats['hp'] = self.stats['max_hp']

            # Play the level-up sound
            if self.level_up_sound:
                self.level_up_sound.play()

        self.update_ui()

    def apply_daily_decay(self):
        today = datetime.now().date()
        last = datetime.fromisoformat(self.stats.get('last_login')).date()
        if today > last:
            days_passed = (today - last).days
            self.stats['strength'] = max(0, self.stats['strength'] - 5 * days_passed)
            self.stats['last_login'] = str(today)
            self.generate_daily_quests()
        elif not self.stats.get('daily_quests'):
            self.generate_daily_quests()

    def generate_daily_quests(self):
        options = [
            {"task": "Do 20 push-ups", "progress": 0, "goal": 20, "type": "push-ups"},
            {"task": "Run 15 times", "progress": 0, "goal": 15, "type": "running"},
            {"task": "Air Bike 10 reps", "progress": 0, "goal": 10, "type": "air bike"},
            {"task": "Do 30 sit-ups", "progress": 0, "goal": 30, "type": "sit-ups"}
        ]
        self.stats['daily_quests'] = random.sample(options, 3)

    def update_ui(self):
        self.status_label.text = self.get_status_text()
        self.exp_bar.value = self.stats['exp']
        self.exp_label.text = f"EXP: {self.stats['exp']}/{self.exp_to_level}"
        self.hp_bar.value = self.stats['hp']
        self.hp_label.text = f"HP: {self.stats['hp']}/{self.stats['max_hp']}"

        for i, quest_label in enumerate(self.daily_quest_labels):
            quest = self.stats['daily_quests'][i]
            quest_label.text = f"{quest['task']} ({quest['progress']}/{quest['goal']})"
            if quest['progress'] >= quest['goal']:
                quest_label.color = (0.2, 0.8, 0.2, 1)  # green to show completed

    def get_status_text(self):
        return (f"Level: {self.stats['level']}\n"
                f"Strength: {self.stats['strength']}  "
                f"Stamina: {self.stats['stamina']}  "
                f"Agility: {self.stats['agility']}")

    def save_progress(self, *args):
        with open(self.save_file, 'w') as f:
            json.dump(self.stats, f)
        popup = Popup(title='Saved', content=Label(text='Progress Saved!'), size_hint=(0.5, 0.3))
        popup.open()

    def load_progress(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                self.stats.update(json.load(f))

class WorkoutRPGApp(App):
    def build(self):
        return WorkoutRPG()

if __name__ == '__main__':
    WorkoutRPGApp().run()
