from tabulate import tabulate


class Styler:
    def __init__(self):
        pass

    def apply_style(self, text):
        return f"<{self.style}>{text}</{self.style}>"

    # Log the text with format
    def log(self, data, padding=2, format="none"):
        if format == "none":
            print(">>> " + data)
            return

        if format != "box":
            print(f"Invalid format: {format}")
            return

        if format == "table":
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

        # Calculate the width of the box
        box_width = len(data) + 2 * padding

        # Create the top and bottom borders of the box
        top_border = f"╭{'─' * box_width}╮"
        bottom_border = f"╰{'─' * box_width}╯"

        # Create the middle part of the box with padding
        middle = f"│{' ' * padding}{data}{' ' * padding}│"

        # Print the box
        print(top_border)
        print(middle)
        print(bottom_border)
