# Desktop-Notifier

This is a Python desktop reminder application built with the tkinter library.
It allows users to set custom reminders with a title, message, time, and alert sound. The program features:

-A single solid background color (user-requested change)

-Black text for better readability

-Clean alignment using the grid() layout for proper spacing and resizing

-Buttons for starting, pausing, snoozing, and testing reminders

-Daily mode and once-only mode



Key Features
1.Custom Reminder Details
-Title field for the notification heading
-Message field for the notification content
-Time field in 24-hour format (HH:MM)

2.Sound Alert
-Ability to choose a .wav sound file
-"Test Sound” button to check the alert sound

3.Reminder Modes
-Once Mode → Alerts only at the set time
-Daily Mode → Alerts every day at the set time

4.Controls
-Start – Activates the reminder
-Pause – Temporarily stops alerts
-Snooze 5m – Delays the alert by 5 minutes
-Test Now – Instantly shows the notification popup




How It Works
1.User Inputs

  Enter the title and message for the reminder.
  Set the desired time.
  Select the alert sound (optional).

2.Running

  When “Start” is clicked, a loop checks the system time every second.
  If the time matches the set time:
    A popup notification appears with the title and message.
    The sound file plays (if selected).

3.Modes

  Once Mode: Stops after the reminder triggers.
  Daily Mode: Resets and waits for the next day at the same time.

4.Extra Controls

  Pause stops the checking loop without losing the set time.
  Snooze adds 5 minutes to the reminder time.
  Test Now instantly shows the reminder without waiting.
