#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import subprocess

class WindowSwitcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Window Switcher")
        self.root.geometry("600x400")

        # Search bar
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.root, textvariable=self.search_var)
        self.search_entry.pack(pady=10, fill="x", padx=10)
        self.search_entry.bind("<Return>", self.bring_to_foreground)
        self.search_entry.bind("<KeyRelease>", self.update_list)
        self.search_entry.bind("<Escape>", lambda event: self.root.quit())  # Exit on Esc
        # Bind arrow keys for navigation
        self.search_entry.bind("<Up>", self.navigate_list)
        self.search_entry.bind("<Down>", self.navigate_list)
        self.search_entry.bind("<Left>", self.navigate_list)
        self.search_entry.bind("<Right>", self.navigate_list)

        # Listbox to display windows
        self.window_listbox = tk.Listbox(self.root, height=20)
        self.window_listbox.pack(pady=10, fill="both", expand=True, padx=10)

        # Initial population of the window list
        self.windows = self.get_open_windows()
        self.update_list(None)

        # Forcefully set focus to the search entry
        self.root.update()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.search_entry.focus_force()
        self.root.after(100, lambda: self.root.attributes('-topmost', False))

        # Highlight the first item initially
        if self.window_listbox.size() > 0:
            self.window_listbox.select_set(0)
            self.window_listbox.see(0)

    def get_open_windows(self):
        """Get a list of open windows using wmctrl."""
        try:
            output = subprocess.check_output(["wmctrl", "-lx"], text=True)
            windows = []
            for line in output.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 5:
                    win_id = parts[0]  # Window ID in hex
                    class_name = parts[2]  # Class (e.g., gnome-calculator.gnome-calculator)
                    title = " ".join(parts[4:])  # Window title
                    windows.append((win_id, class_name, title))
            return windows
        except subprocess.CalledProcessError:
            return []

    def update_list(self, event):
        """Update the listbox based on the search string, but don't reset highlight for arrows."""
        if event and event.keysym in ("Up", "Down", "Left", "Right"):
            return

        self.window_listbox.delete(0, tk.END)
        search_str = self.search_var.get().lower()

        for win_id, class_name, title in self.windows:
            display_str = f"{win_id} - {class_name} - {title}"
            if not search_str or search_str in display_str.lower():
                self.window_listbox.insert(tk.END, display_str)

        # Highlight the first item after updating the list
        if self.window_listbox.size() > 0:
            self.window_listbox.select_clear(0, tk.END)
            self.window_listbox.select_set(0)
            self.window_listbox.see(0)

    def navigate_list(self, event):
        """Navigate the listbox with arrow keys circularly while keeping focus on search."""
        current = self.window_listbox.curselection()
        total_items = self.window_listbox.size()

        if not current:  # If nothing is selected, select the first item
            if total_items > 0:
                self.window_listbox.select_set(0)
                self.window_listbox.see(0)
            return "break"

        current_index = current[0]

        # Handle arrow key navigation with circular wrapping
        if event.keysym == "Up" or event.keysym == "Left":
            new_index = (current_index - 1) % total_items  # Wrap to bottom if at top
        elif event.keysym == "Down" or event.keysym == "Right":
            new_index = (current_index + 1) % total_items  # Wrap to top if at bottom
        else:
            return  # Ignore other keys

        self.window_listbox.select_clear(0, tk.END)
        self.window_listbox.select_set(new_index)
        self.window_listbox.see(new_index)
        self.search_entry.focus_force()  # Keep focus on search
        return "break"  # Prevent default arrow behavior in Entry

    def bring_to_foreground(self, event=None):
        """Bring the highlighted window to the foreground and exit."""
        selection = self.window_listbox.curselection()
        if selection:
            selected = self.window_listbox.get(selection[0])
            win_id = selected.split()[0]  # Extract the window ID
            try:
                subprocess.run(["wmctrl", "-ia", win_id])
                self.root.quit()  # Close the app after bringing window forward
            except subprocess.CalledProcessError as e:
                print(f"Error bringing window to foreground: {e}")

def main():
    root = tk.Tk()
    app = WindowSwitcher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
