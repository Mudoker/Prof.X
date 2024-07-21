from tabulate import tabulate
import os
from enum import Enum


# Available commands
class COMMAND(Enum):
    SEE_ALL_ORACLE = 1
    SEE_A_TEST = 2
    RUN_A_TEST = 3
    EXIT = 4


# Convert user input to command
def execute_user_input(user_input):
    converted_input = COMMAND(user_input)
    if converted_input == COMMAND.SEE_ALL_ORACLE:
        print("See all the available oracle")
    elif converted_input == COMMAND.SEE_A_TEST:
        print("See a test")
    elif converted_input == COMMAND.RUN_A_TEST:
        print("Run a test")
    elif converted_input == COMMAND.EXIT:
        print("Exiting with status code 0")
        os._exit(0)
    else:
        print("Invalid input! Please enter a valid index.")


# Tabulate the data
def table(data):
    try:
        table = tabulate(
            data,
            headers=["Index", "Function"],
            tablefmt="rounded_grid",
            numalign="center",
        )
        print(table)
    except Exception as e:
        print(f"Logging error: {e}")


# Log the text with format
def log(text, padding=2, format="none"):
    if format == "none":
        print(text)
        return

    if format != "box":
        print(f"Invalid format: {format}")
        return

    # Calculate the width of the box
    box_width = len(text) + 2 * padding

    # Create the top and bottom borders of the box
    top_border = f"╭{'─' * box_width}╮"
    bottom_border = f"╰{'─' * box_width}╯"

    # Create the middle part of the box with padding
    middle = f"│{' ' * padding}{text}{' ' * padding}│"

    # Print the box
    print(top_border)
    print(middle)
    print(bottom_border)


# Main function
def main():
    log("Welcome to X-Men for automed GUI-based testing!", format="box")

    func_array = [
        "See all the available oracle",
        "See a test",
        "Run a test",
        "Exit",
    ]

    # Display the table
    table([(i + 1, func) for i, func in enumerate(func_array)])

    while True:

        try:
            user_input = int(input("Enter the index of the function: "))
            execute_user_input(user_input)
        except ValueError:
            print("Invalid input! Please enter a number.")
            continue


# Call the main function if the script is executed directly
if __name__ == "__main__":
    main()
