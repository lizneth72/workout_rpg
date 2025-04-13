from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.animation import Animation
import json
import os

# Set portrait orientation
Window.size = (480, 800)

class WorkoutRPG(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=20, **kwargs)

        # Load saved data or set defaults
        self.stats = {
            'level': 1,
            'exp': 0,
            'hp': 100,
            'max_hp': 100,
            'strength': 0,
            'stamina': 0,
            'agility': 0,
        }
        self.exp_to_level = 100
        self.save_file = 'rpg_save.json'
        self.load_progress()

        # Labels and bars
        self.status_label = Label(text=self.get_status_text(), font_size=28, size_hint=(1, 0.3), bold=True, color=(0.2, 0.2, 0.2, 1))
        self.hp_bar = ProgressBar(max=self.stats['max_hp'], value=self.stats['hp'], size_hint=(1, 0.07))
        self.hp_label = Label(text=f"HP: {self.stats['hp']}/{self.stats['max_hp']}", size_hint=(1, 0.07), font_size=20)
        self.exp_bar = ProgressBar(max=self.exp_to_level, value=self.stats['exp'], size_hint=(1, 0.07))
        self.exp_label = Label(text=f"EXP: {self.stats['exp']}/{self.exp_to_level}", size_hint=(1, 0.07), font_size=20)

        # Add UI elements
        self.add_widget(self.status_label)
        self.add_widget(self.hp_bar)
        self.add_widget(self.hp_label)
        self.add_widget(self.exp_bar)
        self.add_widget(self.exp_label)

        # Workout buttons
        self.add_workout_button("Push-ups", 'strength')
        self.add_workout_button("Running", 'stamina')
        self.add_workout_button("Air Bike", 'agility')
        self.add_workout_button("Sit-ups", 'stamina')

        # Save button
        save_button = Button(text="Save Game", size_hint=(1, 0.12), font_size=24, background_color=(0.2, 0.6, 0.2, 1))
        save_button.bind(on_press=self.save_progress)
        self.add_widget(save_button)

    def add_workout_button(self, label, stat):
        btn = Button(text=label, size_hint=(1, 0.12), font_size=24, background_color=(0.1, 0.4, 0.8, 1))
        btn.bind(on_press=lambda x: self.animate_button(btn, stat))
        self.add_widget(btn)

    def animate_button(self, button, stat):
        # Simple animation to scale the button and fade
        anim = Animation(size_hint=(1, 0.14), duration=0.1) + Animation(size_hint=(1, 0.12), duration=0.1)
        anim.start(button)
        self.handle_workout(stat)

    def handle_workout(self, stat):
        self.stats[stat] += 1
        self.stats['exp'] += 1
        if self.stats['exp'] >= self.exp_to_level:
            self.stats['level'] += 1
            self.stats['exp'] = 0
            self.stats['hp'] = self.stats['max_hp']

        self.update_ui()

    def update_ui(self):
        self.status_label.text = self.get_status_text()
        self.exp_bar.value = self.stats['exp']
        self.exp_label.text = f"EXP: {self.stats['exp']}/{self.exp_to_level}"
        self.hp_bar.value = self.stats['hp']
        self.hp_label.text = f"HP: {self.stats['hp']}/{self.stats['max_hp']}"

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
                self.stats = json.load(f)

class WorkoutRPGApp(App):
    def build(self):
        return WorkoutRPG()

if __name__ == '__main__':
    WorkoutRPGApp().run()
