import os
import datetime
import pandas as pd
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1txIZgQFE0LMJi1WBs4cS-GejUyBETAyo/export?format=xlsx"

def get_schedule_for_today():
    try:
        response = requests.get(SPREADSHEET_URL)
        response.raise_for_status()
        df = pd.read_excel(response.content, sheet_name="2026-2027", header=None)
    except Exception as e:
        return f"❌ Ошибка при скачивании или чтении таблицы: {e}"

    today_index = datetime.datetime.now().weekday()
    
    if today_index == 6:
        return "🎉 Сегодня воскресенье — пар нет, отдыхайте!"

    days_map = {
        0: "понедельник",
        1: "вторник",
        2: "среда",
        3: "четверг",
        4: "пятница",
        5: "суббота"
    }
    
    target_day = days_map.get(today_index)
    current_day_found = False
    schedule_lines = []
    
    for index, row in df.iterrows():
        cell_value = str(row.iloc[0]).strip().lower()
        
        if target_day in cell_value:
            current_day_found = True
        elif cell_value in ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]:
            if current_day_found:
                break
                
        if current_day_found:
            time_slot = str(row.iloc[1]).strip()
            
            extra_info = []
            for col_idx in [3, 4, 5, 6, 7]:
                val = str(row.iloc[col_idx]).strip() if pd.notna(row.iloc[col_idx]) else ""
                if val and val != "nan" and val not in extra_info:
                    extra_info.append(val)

            if time_slot and time_slot != "nan" and extra_info:
                subject_info = " / ".join(extra_info)
                schedule_lines.append(f"• **{time_slot}**\n  └ {subject_info}")

    if not schedule_lines:
        return f"📅 Сегодня ({target_day.capitalize()}), судя по таблице, пар у 2 группы нет или они не указаны."

    header = f"📅 **Расписание для 2 группы на {target_day.capitalize()}:**\n\n"
    return header + "\n".join(schedule_lines)

def send_telegram_message(text):
    if not TOKEN or not CHAT_ID:
        raise ValueError("Не заданы TELEGRAM_TOKEN или TELEGRAM_CHAT_ID!")
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code
