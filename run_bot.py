import os
import sys
import psutil
import subprocess
from pathlib import Path

def is_bot_running():
    """Проверяет, запущен ли уже экземпляр бота"""
    current_process = psutil.Process()
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if process.pid != current_process.pid and process.info['name'] == 'python.exe':
                cmdline = process.info['cmdline']
                if cmdline and 'bot' in ' '.join(cmdline):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def main():
    if is_bot_running():
        print("❌ Бот уже запущен! Закройте существующий экземпляр перед запуском нового.")
        sys.exit(1)
    
    # Путь к директории с ботом
    bot_dir = Path(__file__).parent / 'bot'
    if not bot_dir.exists():
        print(f"❌ Директория {bot_dir} не найдена!")
        sys.exit(1)
    
    print("🚀 Запуск бота...")
    try:
        # Запускаем бота из директории bot
        subprocess.run([sys.executable, '-m', 'bot'], cwd=str(bot_dir), check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 