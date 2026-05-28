from typing import List
from cli.base import Command


class MenuController:
    def __init__(self, commands: List[Command]):
        self.commands = commands

    def display_menu(self) -> None:
        print("\n" + "=" * 45)
        print("   STUDENT PERFORMANCE ANALYTICS SYSTEM")
        print("=" * 45)
        for i, cmd in enumerate(self.commands, 1):
            print(f"{i}. {cmd.name}")
        print(f"{len(self.commands) + 1}. Exit")
        print("=" * 45)

    def run(self) -> None:
        while True:
            self.display_menu()
            choice = input("Select an option: ").strip()

            exit_option = len(self.commands) + 1
            if choice == str(exit_option):
                print("Goodbye!")
                break

            try:
                index = int(choice) - 1
                if 0 <= index < len(self.commands):
                    self.commands[index].execute()
                else:
                    print(
                        f"[Invalid] Please select a number between 1 and {exit_option}."
                    )
            except ValueError:
                print(f"[Invalid] Please enter a valid number.")

            print("\nPress Enter to return to menu...")
            input()
