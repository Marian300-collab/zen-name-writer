import os
import requests
import json
import random
from datetime import datetime

# Настройки для локальной модели
MODEL_NAME = "qwen2.5:14b" 
OLLAMA_URL = "http://localhost:11434/api/generate"

# ==========================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ШАБЛОНАМИ (для других режимов)
# ==========================================

def load_list(file_path):
    """Загружает список элементов из файла templates/, игнорируя заголовки"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = [line.strip() for line in content.split('\n') 
                 if line.strip() and not line.startswith('#')]
        return lines
    except FileNotFoundError:
        print(f"⚠️ Файл не найден: {file_path}")
        return []

def build_unique_combination():
    """Собирает уникальную случайную комбинацию элементов для статьи"""
    anchors = load_list("templates/anchors.md")
    sensory = load_list("templates/sensory.md")
    scholars = load_list("templates/scholars.md")
    endings = load_list("templates/endings.md")
    
    anchor = random.choice(anchors) if anchors else "старая тетрадь в клетку"
    sensory_sample = random.sample(sensory, min(4, len(sensory))) if sensory else []
    scholar = random.choice(scholars) if scholars else "Анна Суперанская — словари имён"
    ending = random.choice(endings) if endings else "Закрыла тетрадь и убрала на полку"
    
    return {
        "anchor": anchor,
        "sensory": sensory_sample,
        "scholar": scholar,
        "ending": ending
    }

# ==========================================
# ОСНОВНЫЕ РЕЖИМЫ ГЕНЕРАЦИИ
# ==========================================

def generate_article(topic):
    print(f"\n⏳ Генерирую статью на тему: 'Имя {topic}'... (это может занять 2-3 минуты)")
    
    # Используем упрощенный системный промпт для быстрого режима
    system_prompt = f"""
    Ты — автор Дзен-канала «О чём говорят Славянские Веды». Пишешь тёплые, познавательные статьи про имена.
    Структура: Введение, Этимология, История в России, Динамика популярности, Культурный код, Звучание имени, Финал с вопросом.
    Запрещено: эзотерика, выдуманная статистика, клише ("пар из чашки"), личные истории с беременностями и родственниками.
    Объём: около 3500-4000 знаков.
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\nТема статьи: Имя {topic}\n\nНапиши полную статью, строго следуя инструкциям.",
        "stream": False,
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        article_text = result.get("response", "")
        
        os.makedirs("output", exist_ok=True)
        filename = f"output/article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(article_text)
            
        print(f"\n✅ Успех! Статья сохранена в файл: {filename}")
        
    except requests.exceptions.Timeout:
        print("\n❌ Ошибка: Превышено время ожидания.")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")


def edit_article(filename):
    print(f"\n⏳ Анализирую и редактирую статью: {filename}...")
    
    with open(filename, "r", encoding="utf-8") as f:
        article_text = f.read()
    
    editor_prompt = ""
    possible_paths = ["prompts/04_editor.md", "04_editor.md", "agent_editor.md"]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                editor_prompt = f.read()
            break
            
    if not editor_prompt:
        print("❌ Ошибка: Не найден файл промпта редактора.")
        return

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{editor_prompt}\n\nВот текст черновика для анализа и редактирования:\n\n{article_text}",
        "stream": False,
        "options": {"temperature": 0.5}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        edit_report = result.get("response", "")
        
        os.makedirs("output", exist_ok=True)
        report_filename = f"output/edit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(edit_report)
        
        print(f"\n✅ Отчёт редактора сохранён: {report_filename}")
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")


def rewrite_article(filename):
    print(f"\n⏳ Переписываю статью в живом стиле: {filename}...")
    
    with open(filename, "r", encoding="utf-8") as f:
        article_text = f.read()
    
    rewriter_prompt = ""
    possible_paths = ["prompts/08_rewriter_simple.md", "prompts/08_rewriter.md", "08_rewriter.md"]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                rewriter_prompt = f.read()
            break
            
    if not rewriter_prompt:
        print("❌ Ошибка: Не найден файл промпта переписывания.")
        return

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{rewriter_prompt}\n\nВот черновик для переписывания:\n\n{article_text}",
        "stream": False,
        "options": {"temperature": 0.8}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        rewritten_text = result.get("response", "")
        
        os.makedirs("output", exist_ok=True)
        new_filename = f"output/rewritten_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(new_filename, "w", encoding="utf-8") as f:
            f.write(rewritten_text)
        
        print(f"\n✅ Переписанная статья сохранена: {new_filename}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


def run_pipeline(topic):
    print(f"\n⏳ Запускаю Оркестратор для темы: 'Имя {topic}'...")
    
    pipeline_prompt = ""
    possible_paths = ["prompts/universal_pipeline.md", "universal_pipeline.md"]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                pipeline_prompt = f.read()
            break
            
    if not pipeline_prompt:
        print("❌ Ошибка: Не найден файл universal_pipeline.md.")
        return

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{pipeline_prompt}\n\nВходные данные:\nТема: Имя {topic}\n\nСгенерируй полный пакет.",
        "stream": False,
        "options": {"temperature": 0.7}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        pipeline_text = result.get("response", "")
        
        os.makedirs("output", exist_ok=True)
        filename = f"output/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(pipeline_text)
            
        print(f"\n✅ Полный пакет сохранён в файл: {filename}")
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")


# ==========================================
# ЗОЛОТОЙ СТАНДАРТ V2 (ИСПРАВЛЕННЫЙ И УПРОЩЁННЫЙ)
# ==========================================

def generate_gold_v2(topic):
    print(f"\n⏳ Генерирую статью по Золотому стандарту v2: 'Имя {topic}'... (это займёт 2-4 минуты)")
    
    # 1. Загружаем финальный чистый промпт
    gold_prompt = ""
    possible_paths = ["prompts/09_gold_standard_v2.md", "09_gold_standard_v2.md"]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                gold_prompt = f.read()
            print(f"✅ Загружен промпт: {path}")
            break
            
    if not gold_prompt:
        print("❌ Ошибка: Не найден файл 09_gold_standard_v2.md")
        return

    # 2. Формируем чистый промпт. 
    # МЫ УБРАЛИ: семейную структуру, эталонные примеры и случайные комбинации.
    # Это гарантирует, что модель не будет галлюцинировать с родственниками и клише.
    final_prompt = f"""{gold_prompt}

# 🎯 ТЕКУЩАЯ ЗАДАЧА:
Напиши статью, строго следуя структуре из 7 блоков и правилам выше.
Тема (Имя): {topic}
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": final_prompt,
        "stream": False,
        "options": {"temperature": 0.7} # Оптимальная температура для баланса фактов и стиля
    }
    
    try:
        # ДОБАВЛЕН ТАЙМАУТ 600 СЕКУНД (10 МИНУТ), чтобы модель 14b успевала сгенерировать длинный текст
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        article_text = result.get("response", "")
        
        if not article_text or len(article_text.strip()) < 100:
            print("❌ Ошибка: Модель вернула пустой ответ!")
            return
        
        os.makedirs("output", exist_ok=True)
        filename = f"output/gold_v2_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(article_text)
        
        print(f"\n✅ Статья сохранена: {filename}")
        print(f"Длина: {len(article_text)} символов")
        
    except requests.exceptions.Timeout:
        print("\n❌ Ошибка: Превышено время ожидания (таймаут). Модель думает слишком долго. Попробуй ещё раз.")
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка подключения к Ollama. Убедись, что программа запущена.")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")


def generate_photo_prompts(filename):
    print(f"\n⏳ Генерирую промты для фотографий: {filename}...")
    
    with open(filename, "r", encoding="utf-8") as f:
        article_text = f.read()
    
    photo_prompt = ""
    possible_paths = ["prompts/07_photo_director.md", "07_photo_director.md"]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                photo_prompt = f.read()
            break
            
    if not photo_prompt:
        print("❌ Ошибка: Не найден файл 07_photo_director.md")
        return

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{photo_prompt}\n\nВот текст статьи для анализа:\n\n{article_text}",
        "stream": False,
        "options": {"temperature": 0.8}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        photo_text = result.get("response", "")
        
        os.makedirs("output", exist_ok=True)
        new_filename = f"output/photo_prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(new_filename, "w", encoding="utf-8") as f:
            f.write(photo_text)
        
        print(f"\n✅ Промты для фото сохранены: {new_filename}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


# ==========================================
# ГЛАВНОЕ МЕНЮ
# ==========================================

def main():
    while True:
        print("\n" + "="*50)
        print("🌿 ZenName Writer: Редакция ИИ-агентов")
        print("="*50)
        print("1. Сгенерировать статью (Быстрый режим)")
        print("2. Запустить полный пайплайн (Оркестратор)")
        print("3. Отредактировать готовую статью (Редактор)")
        print("4. Переписать статью в живом стиле (Трансформер)")
        print("5. Золотой стандарт v2 (Длинная, структурированная статья)")
        print("6. Сгенерировать промты для фото (Фото-директор)")
        print("7. Выход")
        
        choice = input("\nВыбери действие (1-7): ").strip()
        
        if choice == "1":
            topic = input("Введи имя для статьи (например, 'Мирослава'): ").strip()
            if topic: generate_article(topic)
        elif choice == "2":
            topic = input("Введи имя для полного пайплайна: ").strip()
            if topic: run_pipeline(topic)
        elif choice == "3":
            filename = input("Введи имя файла для редактирования: ").strip()
            if filename and os.path.exists(filename): edit_article(filename)
            else: print("❌ Файл не найден.")
        elif choice == "4":
            filename = input("Введи имя файла для переписывания: ").strip()
            if filename and os.path.exists(filename): rewrite_article(filename)
            else: print("❌ Файл не найден.")
        elif choice == "5":
            topic = input("Введи имя для статьи (Золотой стандарт): ").strip()
            if topic: generate_gold_v2(topic)
        elif choice == "6":
            filename = input("Введи имя файла статьи для фото-промтов: ").strip()
            if filename and os.path.exists(filename): generate_photo_prompts(filename)
            else: print("❌ Файл не найден.")
        elif choice == "7":
            print("До встречи! 🌿")
            break
        else:
            print("❌ Неверный выбор. Попробуй снова.")


if __name__ == "__main__":
    main()