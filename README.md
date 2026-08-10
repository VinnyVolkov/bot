# 🍽️ Bot Food — Telegram Menu Bot

## 📌 Project Overview

**Bot Food** is a Python-based Telegram bot designed to automate the weekly collection of meal information from users.

The bot automatically sends a Google Form, allows users to choose when they want to be reminded, tracks form completion, and provides the administrator with information about users who have not completed the form.

The project was created to automate a repetitive administrative process and reduce the need for manual reminders.

---

## 🚀 Features

- 📋 **Weekly Google Form distribution**
  - Automatically sends the form to registered users every week.
  - Users can open the form directly from Telegram.

- ⏰ **Custom reminders**
  - Users can choose when they want to receive a reminder:
    - 30 minutes
    - 1 hour
    - 2 hours
  - If the user does not select a reminder time, an automatic reminder is scheduled after 3 hours.

- ✅ **Completion tracking**
  - Users can confirm that they have completed the form.
  - Once confirmed, further reminders are stopped.

- 🔄 **Automatic reminders**
  - The bot periodically checks scheduled reminders and sends notifications when necessary.

- 👨‍💼 **Administrator functionality**
  - The administrator receives weekly notifications.
  - The administrator can update the Google Form link.
  - The administrator receives information about users who have not completed the form.

- 📅 **Automatic scheduling**
  - Weekly tasks are executed automatically according to a predefined schedule.

---

## 🛠️ Technologies

- **Python**
- **pyTelegramBotAPI**
- **Schedule**
- **python-dotenv**
- **Telegram Bot API**
- **Google Forms**
- **PyCharm**

---

## ⚙️ How It Works

### 1. User registration

When a user starts the bot, their Telegram ID is added to the list of registered users.

### 2. Weekly form distribution

The bot automatically sends the Google Form to registered users.

The message contains options that allow the user to:

- open the form;
- confirm completion;
- choose a reminder time.

### 3. Reminder system

If the user chooses a reminder, the bot stores the selected time and sends a notification later.

Available reminder options include:

- **30 minutes**
- **1 hour**
- **2 hours**

If the user does not choose a specific reminder time, the default reminder is sent after **3 hours**.

### 4. Completion confirmation

After completing the form, the user can confirm completion through Telegram.

The bot then updates the user's status and stops further reminders.

### 5. Administrator notifications

The bot provides the administrator with information about the current status of form completion.

The administrator can also update the Google Form link directly through the bot.

---

## 📅 Automated Schedule

The bot uses the `schedule` library to perform recurring tasks automatically.

| Time | Action |
|---|---|
| Friday 10:00 | Administrator reminder |
| Friday 17:00 | Weekly Google Form distribution |
| Sunday 14:00 | Form completion status summary |
| Every minute | Reminder status check |

---

## 📁 Project Structure

```text
Bot Food/
│
├── food.py
├── requirements.txt
├── .gitignore
└── README.md
