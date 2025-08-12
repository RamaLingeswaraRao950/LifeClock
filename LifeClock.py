import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

# Constants
DAYS_IN_YEAR = 365.25
LIFE_EXPECTANCY_YEARS = 90
HEARTBEATS_PER_MIN = 72
BREATHS_PER_MIN = 17
STEPS_PER_DAY = 6000

# Themes
LIGHT_THEME = {"bg": "#ffffff", "fg": "#000000"}
DARK_THEME = {"bg": "#1e1e1e", "fg": "#ffffff"}
current_theme = LIGHT_THEME

birth_datetime = None
update_job = None
pulse_job = None
pulse_on = False

progress_target = 0
pulse_direction = 1
beacon_phase = 0


class CenteredDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, prompt="", currency="₹"):
        self.prompt = prompt
        self.currency = currency
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt).pack(pady=5)
        self.entry = tk.Entry(master)
        self.entry.pack(pady=5)
        return self.entry

    def apply(self):
        self.result = self.entry.get()

    def center(self):
        self.update_idletasks()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def wait_visibility(self, window=None):
        super().wait_visibility(window)
        self.center()


def is_leap_year(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def count_leap_days_between(start_dt, end_dt):
    if end_dt < start_dt:
        return 0
    count = 0
    start_year = start_dt.year
    end_year = end_dt.year
    for year in range(start_year, end_year + 1):
        if is_leap_year(year):
            feb29 = datetime(year, 2, 29)
            if start_dt <= feb29 <= end_dt:
                count += 1
    return count


def blend_color(c1, c2, t):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def set_progress_bar_color(percent, beacon_override=None):
    if beacon_override:
        style.configure("Beacon.Horizontal.TProgressbar",
                        troughcolor=current_theme["bg"], background=beacon_override)
        progress_bar.config(style="Beacon.Horizontal.TProgressbar")
        return

    if percent < 50:
        style.configure("Green.Horizontal.TProgressbar",
                        troughcolor=current_theme["bg"], background="#4caf50")
        progress_bar.config(style="Green.Horizontal.TProgressbar")
    elif percent < 80:
        style.configure("Yellow.Horizontal.TProgressbar",
                        troughcolor=current_theme["bg"], background="#ff9800")
        progress_bar.config(style="Yellow.Horizontal.TProgressbar")
    else:
        style.configure("Red.Horizontal.TProgressbar",
                        troughcolor=current_theme["bg"], background="#f44336")
        progress_bar.config(style="Red.Horizontal.TProgressbar")


def animate_progress():
    current_value = progress_bar["value"]
    if abs(current_value - progress_target) > 0.5:
        step = (progress_target - current_value) / 10
        progress_bar["value"] = current_value + step
        root.after(30, animate_progress)
    else:
        progress_bar["value"] = progress_target


def pulse_beacon():
    global pulse_direction, beacon_phase, pulse_job
    if progress_target >= 80:
        beacon_phase = (beacon_phase + 2) % 200
        t = beacon_phase / 100
        if t > 1:
            t = 2 - t
        beacon_color = blend_color("#f44336", "#ffcc00", t)
        set_progress_bar_color(progress_target, beacon_override=beacon_color)
        pulse_job = root.after(75, pulse_beacon)
    else:
        set_progress_bar_color(progress_target)
        if pulse_job:
            root.after_cancel(pulse_job)


def update_display():
    global update_job, progress_target, pulse_job
    if not birth_datetime:
        return

    now = datetime.now()
    diff = now - birth_datetime
    total_seconds = diff.total_seconds()
    total_days = diff.days

    leap_count = count_leap_days_between(birth_datetime, now)
    years_float = total_days / DAYS_IN_YEAR
    months = int(years_float * 12)
    hours = int(total_seconds // 3600)
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds)
    milliseconds = int(total_seconds * 1000)

    results_text.configure(state="normal")
    results_text.delete(1.0, tk.END)
    results_text.insert(tk.END, "📊 You are approximately:\n", "title")
    results_text.insert(tk.END, f"  • Leap years : {leap_count:,}\n", "normal")
    results_text.insert(
        tk.END, f"  • Years (approx)     : {years_float:,.6f}\n", "normal")
    results_text.insert(
        tk.END, f"  • Months (approx)    : {months:,}\n", "normal")
    results_text.insert(
        tk.END, f"  • Days               : {total_days:,}\n", "normal")
    results_text.insert(
        tk.END, f"  • Hours              : {hours:,}\n", "normal")
    results_text.insert(
        tk.END, f"  • Minutes            : {minutes:,}\n", "normal")
    results_text.insert(
        tk.END, f"  • Seconds            : {seconds:,}\n", "normal")
    results_text.insert(
        tk.END, f"  • Milliseconds       : {milliseconds:,}\n\n", "normal")

    results_text.insert(tk.END, "💡 Fun Facts:\n", "title")
    heartbeats = int(minutes * HEARTBEATS_PER_MIN)
    breaths = int(minutes * BREATHS_PER_MIN)
    steps = total_days * STEPS_PER_DAY
    results_text.insert(
        tk.END, f"  • Heartbeats total   : {heartbeats:,} ❤️\n", "normal")
    results_text.insert(
        tk.END, f"  • Breaths total      : {breaths:,} 🌬️\n", "normal")
    results_text.insert(
        tk.END, f"  • Steps approx       : {steps:,} 🚶\n", "normal")
    results_text.insert(
        tk.END, f"  • Estimated pulse    : {HEARTBEATS_PER_MIN} bpm (avg) \n", "normal")
    results_text.configure(state="disabled")

    progress_percent = min((years_float / LIFE_EXPECTANCY_YEARS) * 100, 100)
    set_progress_bar_color(progress_percent)
    progress_target = progress_percent
    animate_progress()

    if progress_percent >= 80:
        if not pulse_job:
            pulse_beacon()
    else:
        if pulse_job:
            try:
                root.after_cancel(pulse_job)
            except Exception:
                pass

    progress_label.config(
        text=f"Life Progress: {progress_percent:.2f}% toward {LIFE_EXPECTANCY_YEARS} years")
    update_job = root.after(1000, update_display)


def calculate_from_years(age_years):
    today = datetime.now()
    return today - timedelta(days=age_years * DAYS_IN_YEAR)


def calculate_from_birthdate(birthdate_str):
    try:
        return datetime.strptime(birthdate_str, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror(
            "Invalid Date", "Please enter date in DD-MM-YYYY format.")
        return None


def calculate_years_mode():
    global birth_datetime
    try:
        if update_job:
            root.after_cancel(update_job)
    except Exception:
        pass
    try:
        age = float(age_entry.get())
        if age < 0:
            raise ValueError
        birth_datetime = calculate_from_years(age)
        update_display()
    except ValueError:
        messagebox.showerror(
            "Invalid Input", "Please enter a valid positive number for age.")


def calculate_birthdate_mode():
    global birth_datetime
    try:
        if update_job:
            root.after_cancel(update_job)
    except Exception:
        pass
    bdate = birthdate_entry.get()
    result = calculate_from_birthdate(bdate)
    if result:
        birth_datetime = result
        update_display()


def style_button(btn, bg, fg, hover_bg=None):
    btn.configure(bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                  relief="flat", font=("Segoe UI", 10, "bold"), bd=0)

    def on_enter(e, b=btn, hb=hover_bg or bg):
        b.configure(font=("Segoe UI", 11, "bold"), bg=hb)

    def on_leave(e, b=btn, bbg=bg):
        b.configure(font=("Segoe UI", 10, "bold"), bg=bbg)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


def toggle_theme():
    global current_theme
    current_theme = DARK_THEME if current_theme == LIGHT_THEME else LIGHT_THEME
    apply_theme(root)


def apply_theme(widget):
    try:
        widget.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    except Exception:
        pass
    for child in widget.winfo_children():
        apply_theme(child)
    try:
        results_text.configure(bg=current_theme["bg"], fg=current_theme["fg"],
                               insertbackground=current_theme["fg"])
    except Exception:
        pass
    try:
        set_progress_bar_color(progress_bar["value"])
    except Exception:
        pass


# GUI Setup
root = tk.Tk()
root.title("⏳ LifeClock ⏳ – Your lifetime, in motion")

window_width = 525
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_pos = (screen_width // 2) - (window_width // 2)
y_pos = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

style = ttk.Style()
style.theme_use("default")

try:
    logo_img = tk.PhotoImage(file="logo.png")
    logo_label = tk.Label(root, image=logo_img, bg=LIGHT_THEME["bg"])
    logo_label.pack(pady=(10, 0))
except Exception:
    pass

title_label = tk.Label(root, text="⏳ LifeClock ⏳ – Your lifetime, in motion",
                       font=("Segoe UI", 14, "bold"), bg=LIGHT_THEME["bg"], fg=LIGHT_THEME["fg"])
title_label.pack(pady=(5, 0))

tagline_label = tk.Label(root, text="See your life in numbers — every heartbeat counts !",
                         font=("Segoe UI", 10, "italic"), bg=LIGHT_THEME["bg"], fg="#555555")
tagline_label.pack(pady=(0, 10))

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", pady=10, padx=10)

# --- Center-aligned From Age in Years ---
frame_years = tk.Frame(notebook)
notebook.add(frame_years, text="From your age")
years_inner = tk.Frame(frame_years)
years_inner.pack(expand=True)
tk.Label(years_inner, text="Enter your age (years)").pack(pady=6)
age_entry = tk.Entry(years_inner)
age_entry.pack(pady=6)
btn_calc_years = tk.Button(
    years_inner, text="Calculate", command=calculate_years_mode)
btn_calc_years.pack(pady=9)
style_button(btn_calc_years, bg="#4CAF50", fg="#ffffff", hover_bg="#45a049")

# --- Center-aligned From Birthdate ---
frame_birthdate = tk.Frame(notebook)
notebook.add(frame_birthdate, text="From your DOB")
birth_inner = tk.Frame(frame_birthdate)
birth_inner.pack(expand=True)
tk.Label(birth_inner, text="Enter your DOB (DD-MM-YYYY)").pack(pady=6)
birthdate_entry = tk.Entry(birth_inner)
birthdate_entry.pack(pady=6)
btn_calc_birth = tk.Button(
    birth_inner, text="Calculate", command=calculate_birthdate_mode)
btn_calc_birth.pack(pady=9)
style_button(btn_calc_birth, bg="#E50C0C", fg="#ffffff", hover_bg="#E40707")

results_frame = tk.Frame(root, bd=1, relief="flat")
results_frame.pack(fill="both", expand=True, padx=10, pady=6)

scrollbar = tk.Scrollbar(results_frame, orient="vertical")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

results_text = tk.Text(results_frame, wrap="word",
                       yscrollcommand=scrollbar.set, font=("Segoe UI", 12))
results_text.pack(fill="both", expand=True)
scrollbar.config(command=results_text.yview)

results_text.tag_configure("title", font=("Segoe UI", 14, "bold"))
results_text.tag_configure("normal", font=("Segoe UI", 12))

pulse_frame = tk.Frame(root)
pulse_frame.pack(pady=6)
pulse_label = tk.Label(pulse_frame, text="❤ Pulse", font=("Segoe UI", 12))
style_button(pulse_label, bg=current_theme["bg"], fg="#d32f2f")

progress_label = tk.Label(root, text=f"Life Progress: 0% toward {LIFE_EXPECTANCY_YEARS} years",
                          font=("Segoe UI", 11))
progress_label.pack(pady=6)
progress_bar = ttk.Progressbar(
    root, orient="horizontal", length=520, mode="determinate")
progress_bar.pack(pady=6)

controls_frame = tk.Frame(root)
controls_frame.pack(pady=8)

btn_theme = tk.Button(
    controls_frame, text="Toggle Dark/Light Mode", command=toggle_theme)
btn_theme.pack(side="left", padx=6)
style_button(btn_theme, bg="#607D8B", fg="#ffffff", hover_bg="#455A64")

btn_help = tk.Button(controls_frame, text="About",
                     command=lambda: messagebox.showinfo(
                         "About", "LifeClock ⏳ – Your lifetime, in motion.\nDisplays your approximate age in many units and fun stats."
                     ))
btn_help.pack(side="left", padx=6)
style_button(btn_help, bg="#009688", fg="#ffffff", hover_bg="#00796B")

set_progress_bar_color(0)
apply_theme(root)
root.mainloop()
