import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
import random
import pickle
from datetime import date

kivy.require('2.0.0')  # Ensure Kivy is installed

class WorkoutRPGApp(App):
    def build(self):
        self.load_progress()

        self.level = self.data.get('level', 1)
        self.exp = self.data.get('exp', 0)
        self.max_exp = 100  # Fixed EXP requirement per level
        self.strength = self.data.get('strength', 0)
        self.stamina = self.data.get('stamina', 0)
        self.agility = self.data.get('agility', 0)
        self.skill_points = self.data.get('skill_points', 0)
        self.health = self.data.get('health', 100)
        self.max_health = self.data.get('max_health', 100)
        self.last_quest_date = self.data.get('last_quest_date', str(date.today()))
        self.daily_quest = self.data.get('daily_quest', None)
        
        # Root layout for the app
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Header with title
        title_label = Label(text="Workout RPG", font_size=36, bold=True, size_hint=(None, None), size=(400, 50))
        title_label.color = (0.9, 0.9, 0.3, 1)
        layout.add_widget(title_label)

        # Character and stats layout
        stats_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=200)
        
        # Left section with character and health bar
        character_section = BoxLayout(orientation='vertical', size_hint_x=None, width=200, spacing=10)
        character_label = Label(text="Character", font_size=24, bold=True, size_hint=(None, None), size=(200, 50))
        self.health_label = Label(text=f"HP: {self.health}/{self.max_health}", font_size=18)
        self.health_bar = ProgressBar(max=self.max_health, value=self.health, size_hint=(None, None), size=(200, 30))
        
        character_section.add_widget(character_label)
        character_section.add_widget(self.health_label)
        character_section.add_widget(self.health_bar)

        # Right section with stats and EXP progress
        stats_section = BoxLayout(orientation='vertical', spacing=10, size_hint_x=None, width=300)
        self.level_label = Label(text=f"Level: {self.level}", font_size=20)
        self.exp_label = Label(text=f"EXP: {self.exp}/{self.max_exp}", font_size=18)
        self.strength_label = Label(text=f"Strength: {self.strength}", font_size=18)
        self.stamina_label = Label(text=f"Stamina: {self.stamina}", font_size=18)
        self.agility_label = Label(text=f"Agility: {self.agility}", font_size=18)
        self.skill_points_label = Label(text=f"Skill Points: {self.skill_points}", font_size=18)
        
        stats_section.add_widget(self.level_label)
        stats_section.add_widget(self.exp_label)
        stats_section.add_widget(self.strength_label)
        stats_section.add_widget(self.stamina_label)
        stats_section.add_widget(self.agility_label)
        stats_section.add_widget(self.skill_points_label)

        stats_layout.add_widget(character_section)
        stats_layout.add_widget(stats_section)

        # Add the stats layout to the main layout
        layout.add_widget(stats_layout)

        # Buttons for workouts
        workout_buttons = [
            ("Push-ups", "strength"),
            ("Running", "stamina"),
            ("Air Bike", "agility"),
            ("Sit-ups", "stamina")
        ]
        
        workout_layout = BoxLayout(orientation='horizontal', spacing=20)
        for workout in workout_buttons:
            button = Button(text=f"{workout[0]} (+1 {workout[1]})", background_color=(0.2, 0.7, 0.2, 1), size_hint=(None, None), size=(200, 50))
            button.bind(on_press=lambda btn, workout_type=workout[1]: self.handle_workout(workout_type))
            workout_layout.add_widget(button)
        
        layout.add_widget(workout_layout)

        # Skill point allocation button
        allocate_button = Button(text="Allocate Skill Point", background_color=(0.8, 0.6, 0.2, 1), size_hint=(None, None), size=(250, 50))
        allocate_button.bind(on_press=self.allocate_skill_point)
        layout.add_widget(allocate_button)

        # Save progress button
        save_button = Button(text="Save Progress", background_color=(0.5, 0.2, 0.5, 1), size_hint=(None, None), size=(250, 50))
        save_button.bind(on_press=self.save_progress)
        layout.add_widget(save_button)

        # Random event button
        random_event_button = Button(text="Trigger Random Event", background_color=(0.9, 0.3, 0.3, 1), size_hint=(None, None), size=(250, 50))
        random_event_button.bind(on_press=self.trigger_random_event)
        layout.add_widget(random_event_button)

        # Daily Quest button
        daily_quest_button = Button(text="Daily Quest", background_color=(0.6, 0.4, 0.8, 1), size_hint=(None, None), size=(250, 50))
        daily_quest_button.bind(on_press=self.handle_daily_quest)
        layout.add_widget(daily_quest_button)

        return layout

    def handle_workout(self, stat_type):
        # Increment the appropriate stat based on the workout type
        if stat_type == "strength":
            self.strength += 1
        elif stat_type == "stamina":
            self.stamina += 1
        elif stat_type == "agility":
            self.agility += 1

        # Gain experience
        self.exp += 1
        if self.exp >= self.max_exp:
            self.level_up()

        # Update UI after workout
        self.update_ui()

    def level_up(self):
        # Level up the character and allocate skill points
        self.level += 1
        self.exp = 0
        self.skill_points += 1
        self.max_exp = 100  # Fixed EXP requirement for each level-up

        # Refill health to max after level-up
        self.health = self.max_health

        # Save progress after leveling up
        self.save_progress()

    def allocate_skill_point(self, instance):
        # Allocate a skill point to strength, stamina, or agility
        if self.skill_points > 0:
            self.strength += 1  # Example: Always allocate to strength for simplicity
            self.skill_points -= 1
        else:
            self.show_popup("No Skill Points", "You don't have any skill points to allocate.")

        self.update_ui()

    def update_ui(self):
        # Update the UI labels and progress bar
        self.level_label.text = f"Level: {self.level}"
        self.exp_label.text = f"EXP: {self.exp}/{self.max_exp}"
        self.strength_label.text = f"Strength: {self.strength}"
        self.stamina_label.text = f"Stamina: {self.stamina}"
        self.agility_label.text = f"Agility: {self.agility}"
        self.skill_points_label.text = f"Skill Points: {self.skill_points}"
        self.health_label.text = f"HP: {self.health}/{self.max_health}"
        self.health_bar.value = self.health

    def trigger_random_event(self, instance):
        # Trigger a random event (for simplicity, just a basic event)
        event = random.choice(["Bonus EXP! You gained 5 extra EXP.", "Healing! You restored 10 health.", "Encountered a monster! Lose 10 health."])
        if "Lose 10 health" in event:
            self.health -= 10  # Decrease health when a monster is encountered
            if self.health < 0:
                self.health = 0  # Prevent health from going negative
        elif "Healing" in event:
            self.health = self.max_health  # Restore health to max
        elif "Bonus EXP" in event:
            self.exp += 5  # Add bonus experience

        self.show_popup("Random Event", event)

        # Update the UI after a random event
        self.update_ui()

    def show_popup(self, title, message):
        # Show a popup with the event message
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def save_progress(self, instance=None):
        # Save current progress to a file using pickle
        with open('progress.pkl', 'wb') as f:
            pickle.dump({
                'level': self.level,
                'exp': self.exp,
                'max_exp': self.max_exp,
                'strength': self.strength,
                'stamina': self.stamina,
                'agility': self.agility,
                'skill_points': self.skill_points,
                'health': self.health,
                'max_health': self.max_health,
                'last_quest_date': self.last_quest_date,
                'daily_quest': self.daily_quest
            }, f)
        self.show_popup("Progress Saved", "Your progress has been saved.")

    def load_progress(self):
        # Load saved progress from a file
        try:
            with open('progress.pkl', 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            # If no save file is found, initialize default values
            self.data = {}

    def handle_daily_quest(self, instance):
        # Check if a new day has started
        current_date = str(date.today())
        if current_date != self.last_quest_date:
            # If a new day, create a new random quest
            self.daily_quest = random.choice(["Do 20 Push-ups", "Run for 10 minutes", "Do 30 Sit-ups"])
            self.last_quest_date = current_date

            self.show_popup("New Daily Quest!", f"Your new daily quest is: {self.daily_quest}")
        else:
            self.show_popup("No New Quest", "You have already completed today's quest.")

if __name__ == '__main__':
    WorkoutRPGApp().run()
