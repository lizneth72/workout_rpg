from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.animation import Animation
from datetime import datetime
import json
import os
import random

# Set portrait orientation
Window.size = (480, 800)

class WorkoutRPG(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=20, **kwargs)

        self.stats = {
            'level': 1,
            'exp': 0,
            'hp': 100,
            'max_hp': 100,
            'strength': 0,
            'stamina': 0,
            'agility': 0,
            'last_login': str(datetime.now().date()),
            'total_reps': 0
        }
        self.exp_to_level = 100
        self.event_cooldown = 40
        self.boss_active = False
        self.boss_hp = 0
        self.save_file = 'rpg_save.json'
        self.load_progress()
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

        self.add_workout_button("Push-ups", 'strength')
        self.add_workout_button("Running", 'stamina')
        self.add_workout_button("Air Bike", 'agility')
        self.add_workout_button("Sit-ups", 'stamina')

        save_button = Button(text="Save Game", size_hint=(1, 0.12), font_size=24, background_color=(0.2, 0.6, 0.2, 1))
        save_button.bind(on_press=self.save_progress)
        self.add_widget(save_button)

    def add_workout_button(self, label, stat):
        btn = Button(text=label, size_hint=(1, 0.12), font_size=24, background_color=(0.1, 0.4, 0.8, 1))
        btn.bind(on_press=lambda x: self.animate_button(btn, stat))
        self.add_widget(btn)

    def animate_button(self, button, stat):
        anim = Animation(size_hint=(1, 0.14), duration=0.1) + Animation(size_hint=(1, 0.12), duration=0.1)
        anim.start(button)
        self.handle_workout(stat)

    def handle_workout(self, stat):
        if self.boss_active:
            return  # Don't allow workouts during boss fight
    
        self.stats[stat] += 1
        self.stats['exp'] += 1
        self.stats['total_reps'] += 1
        if self.stats['exp'] >= self.exp_to_level:
            self.stats['level'] += 1
            self.stats['exp'] = 0
            self.stats['max_hp'] += 1
            self.stats['hp'] = self.stats['max_hp']
    
        if self.stats['total_reps'] > self.event_cooldown and not self.boss_active:
            if random.random() < 0.1:
                self.trigger_boss_fight()
                return
            elif random.random() < 0.15:
                self.trigger_event()
    
        self.update_ui()

    def trigger_boss_fight(self):
        self.boss_hp = random.randint(10, 30)
        self.boss_active = True
        self.ask_for_reps()

    def ask_for_reps(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text=f"Boss appears with {self.boss_hp} HP! How many reps did you do?"))
        reps_input = TextInput(hint_text='Enter reps', multiline=False, input_filter='int')
        layout.add_widget(reps_input)
        submit_btn = Button(text='Submit')
        layout.add_widget(submit_btn)
    
        popup = Popup(title='Boss Fight!', content=layout, size_hint=(0.8, 0.6))
    
        def resolve_battle(instance):
            try:
                reps = int(reps_input.text)
                self.boss_hp -= reps
                if self.boss_hp > 0:
                    damage = random.randint(5, 15)
                    self.stats['hp'] = max(0, self.stats['hp'] - damage)
                    result = f"You dealt {reps} damage. Boss has {self.boss_hp} HP left. You took {damage} damage!"
                else:
                    reward = 10
                    self.stats['exp'] += reward
                    result = f"You defeated the boss! +{reward} EXP"
                    self.boss_active = False
                    self.stats['total_reps'] = 0  # Reset cooldown
                popup.dismiss()
                self.update_ui()
                result_popup = Popup(title='Battle Result', content=Label(text=result), size_hint=(0.7, 0.4))
                result_popup.open()
            except ValueError:
                reps_input.text = ''
                reps_input.hint_text = 'Enter a valid number'
    
        submit_btn.bind(on_press=resolve_battle)
        popup.open()

    def trigger_event(self):
        events = ["You found a treasure chest! +5 EXP", "You feel energized! +10 HP"]
        event = random.choice(events)
        if "EXP" in event:
            self.stats['exp'] += 5
        if "HP" in event:
            self.stats['hp'] = min(self.stats['max_hp'], self.stats['hp'] + 10)
        popup = Popup(title='Random Event!', content=Label(text=event), size_hint=(0.7, 0.4))
        popup.open()

    def apply_daily_decay(self):
        today = datetime.now().date()
        last = datetime.fromisoformat(self.stats.get('last_login')).date()
        if today > last:
            days_passed = (today - last).days
            self.stats['strength'] = max(0, self.stats['strength'] - 5 * days_passed)
            self.stats['last_login'] = str(today)

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
                saved_data = json.load(f)
                # Ensure all expected keys exist
                defaults = {
                    'level': 1,
                    'exp': 0,
                    'hp': 100,
                    'max_hp': 100,
                    'strength': 0,
                    'stamina': 0,
                    'agility': 0,
                    'last_login': str(datetime.now().date()),
                    'total_reps': 0
                }
                for key, value in defaults.items():
                    if key not in saved_data:
                        saved_data[key] = value
                self.stats = saved_data


class WorkoutRPGApp(App):
    def build(self):
        return WorkoutRPG()

if __name__ == '__main__':
    WorkoutRPGApp().run()
