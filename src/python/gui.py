import customtkinter as ctk
from event_repository import load_recent_events
from runway_repository import assign_flight_to_runway, complete_flight
from tkinter import messagebox, simpledialog

from flight_repository import (
    get_active_aircraft,
    load_waiting_flights,
    save_flight
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SmartRunwayApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Runway | Airport Control Center")
        self.geometry("1180x740")
        self.minsize(1000, 650)
        self.configure(fg_color="#0B1220")

        self.db_password = None
        self.aircraft_map = {}
        self.flights = []
        self.displayed_flights = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()
        self.refresh_dashboard()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color="#111B2E"
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="✈  SMART\n    RUNWAY",
            font=("Segoe UI", 21, "bold"),
            text_color="#E7F0FF",
            justify="left"
        ).pack(anchor="w", padx=22, pady=(28, 8))

        ctk.CTkLabel(
            sidebar,
            text="AIRPORT OPERATIONS",
            font=("Segoe UI", 10, "bold"),
            text_color="#7F91AB"
        ).pack(anchor="w", padx=24, pady=(18, 8))

        ctk.CTkLabel(
            sidebar,
            text="●  Runway Dashboard",
            font=("Segoe UI", 14, "bold"),
            text_color="#49D6C8",
            fg_color="#1B2D43",
            corner_radius=8,
            anchor="w",
            padx=12,
            height=42
        ).pack(fill="x", padx=14, pady=4)

        ctk.CTkLabel(
            sidebar,
            text="SCHEDULING",
            font=("Segoe UI", 10, "bold"),
            text_color="#7F91AB"
        ).pack(anchor="w", padx=24, pady=(24, 8))

        ctk.CTkLabel(
            sidebar,
            text="Priority  •  FCFS",
            font=("Segoe UI", 13),
            text_color="#C3D0E2"
        ).pack(anchor="w", padx=26, pady=5)

        ctk.CTkFrame(sidebar, height=1, fg_color="#29384D").pack(
            fill="x", padx=18, pady=(24, 16)
        )

        ctk.CTkLabel(
            sidebar,
            text="Flights are loaded\nfrom smart_runway_db.",
            font=("Segoe UI", 12),
            text_color="#8FA0B8",
            justify="left"
        ).pack(anchor="w", padx=22, pady=4)

    def create_main_area(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=28, pady=24)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Runway Control Center",
            font=("Segoe UI", 27, "bold"),
            text_color="#F1F5FB"
        ).grid(row=0, column=0, sticky="w")

        self.connect_button = ctk.CTkButton(
            header,
            text="Connect MySQL",
            width=150,
            height=38,
            corner_radius=18,
            fg_color="#168F91",
            hover_color="#117779",
            command=self.connect_mysql
        )
        self.connect_button.grid(row=0, column=1, sticky="e")

        stats = ctk.CTkFrame(main, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        for column in range(3):
            stats.grid_columnconfigure(column, weight=1)

        self.total_value = self.create_stat_card(
            stats, 0, "FLIGHTS IN QUEUE", "0", "#59A7FF"
        )
        self.emergency_value = self.create_stat_card(
            stats, 1, "EMERGENCY FLIGHTS", "0", "#FF786F"
        )
        self.wait_value = self.create_stat_card(
            stats, 2, "AVERAGE WAIT", "0 min", "#49D6C8"
        )

        content = ctk.CTkFrame(main, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=3)
        content.grid_rowconfigure(0, weight=1)

        self.create_flight_form(content)
        self.create_queue_panel(content)

    def create_stat_card(self, parent, column, title, value, color):
        card = ctk.CTkFrame(
            parent,
            fg_color="#142035",
            corner_radius=14,
            border_width=1,
            border_color="#25354C"
        )
        card.grid(row=0, column=column, sticky="ew", padx=6, ipady=8)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 11, "bold"),
            text_color="#94A6BF"
        ).pack(anchor="w", padx=18, pady=(14, 4))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 24, "bold"),
            text_color=color
        )
        value_label.pack(anchor="w", padx=18, pady=(0, 12))
        return value_label

    def create_flight_form(self, parent):
        panel = ctk.CTkScrollableFrame(
            parent,
            fg_color="#142035",
            corner_radius=14,
            border_width=1,
            border_color="#25354C"
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Add Flight",
            font=("Segoe UI", 19, "bold"),
            text_color="#F1F5FB"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))

        ctk.CTkLabel(
            panel,
            text="New flights will be saved to MySQL.",
            font=("Segoe UI", 12),
            text_color="#91A2BA"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

        self.add_field_label(panel, "Flight number", 2)
        self.flight_entry = ctk.CTkEntry(
            panel, placeholder_text="Example: AI101", height=38
        )
        self.flight_entry.grid(row=3, column=0, sticky="ew", padx=20)

        self.add_field_label(panel, "Aircraft", 4)
        self.aircraft_box = ctk.CTkComboBox(
            panel,
            values=["Connect to MySQL first"],
            state="disabled",
            height=38
        )
        self.aircraft_box.grid(row=5, column=0, sticky="ew", padx=20)

        self.add_field_label(panel, "Operation", 6)
        self.operation_box = ctk.CTkComboBox(
            panel, values=["Landing", "Takeoff"], state="readonly", height=38
        )
        self.operation_box.set("Landing")
        self.operation_box.grid(row=7, column=0, sticky="ew", padx=20)

        self.add_field_label(panel, "Priority  (1 = highest)", 8)
        self.priority_box = ctk.CTkComboBox(
            panel, values=["1", "2", "3", "4", "5"], state="readonly", height=38
        )
        self.priority_box.set("3")
        self.priority_box.grid(row=9, column=0, sticky="ew", padx=20)

        self.add_field_label(panel, "Emergency", 10)
        self.emergency_box = ctk.CTkComboBox(
            panel, values=["No", "Yes"], state="readonly", height=38
        )
        self.emergency_box.set("No")
        self.emergency_box.grid(row=11, column=0, sticky="ew", padx=20)

        self.add_field_label(panel, "Waiting time (minutes)", 12)
        self.waiting_entry = ctk.CTkEntry(
            panel, placeholder_text="Example: 10", height=38
        )
        self.waiting_entry.insert(0, "0")
        self.waiting_entry.grid(row=13, column=0, sticky="ew", padx=20)

        ctk.CTkButton(
            panel,
            text="+  Add Flight to MySQL",
            height=42,
            corner_radius=9,
            fg_color="#168F91",
            hover_color="#117779",
            font=("Segoe UI", 14, "bold"),
            command=self.add_flight
        ).grid(row=14, column=0, sticky="ew", padx=20, pady=(18, 18))

    def add_field_label(self, parent, text, row):
        ctk.CTkLabel(
            parent,
            text=text,
            text_color="#C3D0E2"
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(10, 4))

    def create_queue_panel(self, parent):
        panel = ctk.CTkFrame(
            parent,
            fg_color="#142035",
            corner_radius=14,
            border_width=1,
            border_color="#25354C"
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            panel,
            text="Flight Queue",
            font=("Segoe UI", 19, "bold"),
            text_color="#F1F5FB"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 2))

        ctk.CTkLabel(
            panel,
            text="Waiting flights from the database appear here.",
            font=("Segoe UI", 12),
            text_color="#91A2BA"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 14))

        controls = ctk.CTkFrame(panel, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))
        controls.grid_columnconfigure(0, weight=1)

        self.method_box = ctk.CTkComboBox(
            controls,
            values=["Priority Scheduling", "FCFS"],
            state="readonly",
            height=38
        )
        self.method_box.set("Priority Scheduling")
        self.method_box.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            controls,
            text="Schedule",
            width=100,
            height=38,
            command=self.schedule_flights
        ).grid(row=0, column=1, padx=(0, 6))

        ctk.CTkButton(
            controls,
            text="Refresh",
            width=85,
            height=38,
            fg_color="#263852",
            hover_color="#344B6B",
            command=self.refresh_from_database
        ).grid(row=0, column=2)

        headings = ctk.CTkFrame(panel, fg_color="#1A2A41", corner_radius=8)
        headings.grid(row=3, column=0, sticky="new", padx=16, pady=(0, 5))

        for column, text in enumerate(
            ["#", "FLIGHT", "OPERATION", "AIRCRAFT", "PRIORITY", "STATUS"]
        ):
            ctk.CTkLabel(
                headings,
                text=text,
                font=("Segoe UI", 10, "bold"),
                text_color="#92A5BF"
            ).grid(row=0, column=column, padx=7, pady=10, sticky="w")

        self.rows = ctk.CTkScrollableFrame(
            panel, fg_color="transparent", corner_radius=8
        )
        self.rows.grid(row=4, column=0, sticky="nsew", padx=16, pady=(0, 12))

        footer = ctk.CTkFrame(panel, fg_color="transparent")
        footer.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 14))
        footer.grid_columnconfigure(0, weight=1)

        self.schedule_message = ctk.CTkLabel(
            footer,
            text="Connect to MySQL first.",
            font=("Segoe UI", 11),
            text_color="#91A2BA"
        )
        self.schedule_message.grid(row=0, column=0, sticky="w", padx=4)

        ctk.CTkButton(
            footer,
            text="Assign Next Runway",
            width=145,
            height=34,
            fg_color="#168F91",
            hover_color="#117779",
            command=self.assign_next_runway
        ).grid(row=0, column=1, padx=(8, 0))       
        ctk.CTkButton(
            footer,
            text="Recent Activity",
            width=130,
            height=34,
            fg_color="#263852",
            hover_color="#344B6B",
            command=self.show_recent_activity
        ).grid(row=0, column=2, padx=(8, 0))
    def connect_mysql(self):
        password = simpledialog.askstring(
            "Connect to MySQL",
            "MySQL root password:",
            show="*",
            parent=self
        )
        if password is None:
            return

        try:
            aircraft = get_active_aircraft(password)
            self.db_password = password
            self.aircraft_map = {
                f'{item["registration_number"]} — {item["aircraft_model"]}':
                    item["aircraft_id"]
                for item in aircraft
            }

            labels = list(self.aircraft_map.keys())
            if labels:
                self.aircraft_box.configure(values=labels, state="readonly")
                self.aircraft_box.set(labels[0])
            else:
                self.aircraft_box.configure(
                    values=["No active aircraft found"],
                    state="disabled"
                )

            self.load_database_flights()
            self.connect_button.configure(
                text="MySQL Connected",
                fg_color="#146B55",
                hover_color="#105641"
            )

            messagebox.showinfo(
                "Connected",
                f"MySQL connected. Loaded {len(self.flights)} waiting flights."
            )

            if not aircraft:
                messagebox.showwarning(
                    "No aircraft found",
                    "Connection works, but active aircraft list is empty. "
                    "Check that seed.sql was run."
                )

        except Exception as error:
            self.db_password = None
            messagebox.showerror("Database connection failed", str(error))

    def load_database_flights(self):
        rows = load_waiting_flights(self.db_password)
        self.flights = []

        for index, row in enumerate(rows):
            self.flights.append({
                "database_id": row[0],
                "number": row[1],
                "operation": row[2].title(),
                "priority": int(row[3]),
                "aircraft": row[4],
                "waiting": max(0, int(row[5] or 0)),
                "emergency": bool(row[6]),
                "order": index
            })

        self.displayed_flights = list(self.flights)
        self.refresh_dashboard()

    def refresh_from_database(self):
        if not self.db_password:
            messagebox.showinfo("Connect first", "Pehle Connect MySQL dabao.")
            return

        try:
            self.load_database_flights()
            self.schedule_message.configure(text="Flight queue refreshed from MySQL.")
        except Exception as error:
            messagebox.showerror("Refresh failed", str(error))

    def add_flight(self):
        if not self.db_password:
            messagebox.showinfo("Connect first", "Flight save karne se pehle MySQL connect karo.")
            return

        number = self.flight_entry.get().strip()
        aircraft_label = self.aircraft_box.get()

        if not number:
            messagebox.showerror("Missing flight number", "Flight number enter karo.")
            return

        if aircraft_label not in self.aircraft_map:
            messagebox.showerror("Select aircraft", "MySQL se ek active aircraft select karo.")
            return

        try:
            waiting = int(self.waiting_entry.get())
            if waiting < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid waiting time",
                "Waiting time 0 ya usse bada whole number hona chahiye."
            )
            return

        flight = {
            "number": number,
            "operation": self.operation_box.get(),
            "priority": int(self.priority_box.get()),
            "emergency": self.emergency_box.get() == "Yes",
            "waiting": waiting
        }

        try:
            save_flight(
                self.db_password,
                flight,
                self.aircraft_map[aircraft_label]
            )
            self.flight_entry.delete(0, "end")
            self.waiting_entry.delete(0, "end")
            self.waiting_entry.insert(0, "0")
            self.load_database_flights()
            self.schedule_message.configure(text=f"{number} saved to MySQL.")
        except Exception as error:
            messagebox.showerror("Could not save flight", str(error))

    def schedule_flights(self):
        if not self.flights:
            messagebox.showinfo("Queue is empty", "MySQL se flights load karne ke liye Refresh dabao.")
            return

        if self.method_box.get() == "FCFS":
            ordered = sorted(
                self.flights,
                key=lambda flight: (
                    not flight["emergency"],
                    flight["order"]
                )
            )
            self.schedule_message.configure(
                text="FCFS: emergency flights first, then database arrival order."
            )
        else:
            ordered = sorted(
                self.flights,
                key=lambda flight: (
                    not flight["emergency"],
                    max(1, flight["priority"] - flight["waiting"] // 15),
                    flight["order"]
                )
            )
            self.schedule_message.configure(
                text="Priority: emergencies first, then priority and waiting time."
            )

        self.displayed_flights = ordered
        self.render_queue()
    def assign_next_runway(self):
        if not self.db_password:
            messagebox.showinfo("Connect first", "Pehle MySQL connect karo.")
            return

        flight = next(
            (
                item for item in self.displayed_flights
                if not item.get("assigned_runway")
            ),
            None
        )

        if not flight:
            messagebox.showinfo(
                "No waiting flights",
                "Assign karne ke liye koi waiting flight nahi hai."
            )
            return

        try:
            runway = assign_flight_to_runway(
                self.db_password,
                flight["database_id"]
            )
            flight["assigned_runway"] = runway
            self.schedule_message.configure(
                text=f'{flight["number"]} assigned to {runway}.'
            )
            self.refresh_dashboard()

        except Exception as error:
            messagebox.showerror("Runway assignment failed", str(error))
    def complete_selected_flight(self, flight):
        if not self.db_password:
            messagebox.showinfo("Connect first", "Pehle MySQL connect karo.")
            return

        if not messagebox.askyesno(
            "Complete flight",
            f'{flight["number"]} ko completed mark karein?'
        ):
            return

        try:
            flight_number, runway = complete_flight(
                self.db_password,
                flight["database_id"]
            )
            flight["completed"] = True
            self.schedule_message.configure(
                text=f"{flight_number} completed on {runway}."
            )
            self.refresh_dashboard()

        except Exception as error:
            messagebox.showerror("Could not complete flight", str(error))        
    def show_recent_activity(self):
        if not self.db_password:
            messagebox.showinfo("Connect first", "Pehle MySQL connect karo.")
            return

        try:
            events = load_recent_events(self.db_password)
        except Exception as error:
            messagebox.showerror("Could not load activity", str(error))
            return

        window = ctk.CTkToplevel(self)
        window.title("Recent Runway Activity")
        window.geometry("620x460")
        window.configure(fg_color="#0B1220")

        ctk.CTkLabel(
            window,
            text="Recent Runway Activity",
            font=("Segoe UI", 22, "bold"),
            text_color="#F1F5FB"
        ).pack(anchor="w", padx=20, pady=(18, 10))

        activity_list = ctk.CTkScrollableFrame(
            window,
            fg_color="#142035",
            corner_radius=12
        )
        activity_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not events:
            ctk.CTkLabel(
                activity_list,
                text="No activity recorded yet.",
                text_color="#91A2BA"
            ).pack(padx=15, pady=20)
            return

        for event in events:
            card = ctk.CTkFrame(activity_list, fg_color="#17263B", corner_radius=8)
            card.pack(fill="x", padx=8, pady=5)

            event_time = event["event_time"]
            if hasattr(event_time, "strftime"):
                event_time = event_time.strftime("%d %b %Y, %I:%M %p")

            flight = event["flight_number"] or "Flight not specified"
            runway = event["runway_code"] or "Runway not specified"

            ctk.CTkLabel(
                card,
                text=f'{event["event_type"]}  •  {flight}  •  {runway}',
                font=("Segoe UI", 12, "bold"),
                text_color="#E7F0FF",
                wraplength=520
            ).pack(anchor="w", padx=12, pady=(10, 2))

            ctk.CTkLabel(
                card,
                text=f'{event_time}  |  {event["details"] or ""}',
                font=("Segoe UI", 11),
                text_color="#91A2BA",
                wraplength=520,
                justify="left"
            ).pack(anchor="w", padx=12, pady=(2, 10))
    def refresh_dashboard(self):
        waiting_flights = [
            flight for flight in self.flights
            if not flight.get("assigned_runway")
        ]

        total = len(waiting_flights)
        emergencies = sum(
            1 for flight in waiting_flights if flight["emergency"]
        )
        average_wait = (
            round(
                sum(flight["waiting"] for flight in waiting_flights) / total
            )
            if total else 0
        )

        self.total_value.configure(text=str(total))
        self.emergency_value.configure(text=str(emergencies))
        self.wait_value.configure(text=f"{average_wait} min")
        self.render_queue()

    def render_queue(self):
        for widget in self.rows.winfo_children():
            widget.destroy()

        if not self.displayed_flights:
            ctk.CTkLabel(
                self.rows,
                text="No waiting flights. Connect or press Refresh.",
                text_color="#91A2BA"
            ).grid(row=0, column=0, padx=20, pady=30)
            return

        for index, flight in enumerate(self.displayed_flights, start=1):
            row = ctk.CTkFrame(self.rows, fg_color="#17263B", corner_radius=8)
            row.grid(row=index - 1, column=0, sticky="ew", pady=4)

            values = [
                str(index),
                flight["number"],
                flight["operation"],
                flight["aircraft"],
                str(flight["priority"])
            ]

            for column, value in enumerate(values):
                ctk.CTkLabel(
                    row,
                    text=value,
                    text_color="#E7F0FF" if column == 1 else "#C3D0E2",
                    font=("Segoe UI", 11, "bold") if column == 1 else ("Segoe UI", 11)
                ).grid(row=0, column=column, padx=7, pady=12, sticky="w")

            emergency = flight["emergency"]
            runway = flight.get("assigned_runway")

            if runway:
                badge_text = f"ASSIGNED {runway}"
                badge_color = "#66D7E5"
                badge_background = "#173B45"
            elif emergency:
                badge_text = "EMERGENCY"
                badge_color = "#FF9189"
                badge_background = "#3A222A"
            else:
                badge_text = "NORMAL"
                badge_color = "#65D6A5"
                badge_background = "#19352E"

            ctk.CTkLabel(
                row,
                text=badge_text,
                font=("Segoe UI", 9, "bold"),
                text_color=badge_color,
                fg_color=badge_background,
                corner_radius=12,
                padx=7,
                pady=5
            ).grid(row=0, column=5, padx=6)
            if runway and not flight.get("completed"):
                ctk.CTkButton(
                    row,
                    text="Complete",
                    width=78,
                    height=28,
                    fg_color="#168F91",
                    hover_color="#117779",
                    command=lambda item=flight:
                        self.complete_selected_flight(item)
                ).grid(row=0, column=6, padx=(4, 8))            
if __name__ == "__main__":
    app = SmartRunwayApp()
    app.mainloop()