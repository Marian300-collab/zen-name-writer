import os
import requests
import json
from datetime import datetime

# Настройки для слабой видеокарты (используем легкую модель)
# Если у тебя стоит другая, поменяй 'gemma4:e4b' на название твоей модели (например, 'phi3' или 'llama3.2:1b')
MODEL_NAME = "gemma4:e4b"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Системный промпт (наши строгие правила из .clinerules)
SYSTEM_PROMPT = """
Ты пишешь статью для Дзен-канала об именах (славянских и других, Россия многонациональна).
СТРОГИЕ ЗАПРЕТЫ: Никакой эзотерики ("энергия", "карма", "родовые программы", "места силы", "духовный заряд").
ТОН: Живой, тёплый, доверительный, бытовой. Сенсорные образы, историческая достоверность.
Подписи ("автор статьи", "редакция") КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНЫ.

В КОНЦЕ СТАТЬИ ОБЯЗАТЕЛЬНО добавь три элемента, адаптированных под тему статьи:
1. Вопрос к читателю по теме статьи (для вовлечения в комментарии). Пример: "А вы помните, как выбирали имя своему сыну или дочке, и что оказалось решающим — семейная традиция или просто удачное сочетание с отчеством? Буду рада прочитать ваши истории в комментариях 👇"
2. Короткий дисклеймер по теме. Пример: "Помните, что этот текст — лишь размышление о бытовом выборе, а не строгое историческое или педагогическое руководство. Статистика ЗАГСов даёт общую картину, но в каждой семье своя логика и свои тёплые причины."
3. Призыв подписаться: "Подписывайтесь на канал, чтобы не пропустить новые разборы "
"""

def generate_article(topic):
    print(f"\n⏳ Генерирую статью на тему: '{topic}'... (это может занять 1-2 минуты)")
    
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nНапиши подробную, интересную статью на тему: {topic}",
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        article_text = result.get("response", "")
        
        # Создаем папку output, если её нет
        os.makedirs("output", exist_ok=True)
        
        # Сохраняем в файл
        filename = f"output/article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(article_text)
            
        print(f"\n✅ Успех! Статья сохранена в файл: {filename}")
        return article_text
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка: Не удалось подключиться к Ollama. Убедись, что программа Ollama запущена.")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")

def main():
    print("="*50)
    print("🌿 ZenName Writer: Генератор статей для Дзен")
    print("="*50)
    print("1. Сгенерировать новую статью")
    print("2. Выход")
    
    choice = input("\nВыбери действие (1 или 2): ").strip()
    
    if choice == "1":
        topic = input("Введи тему или имя для статьи (например, 'Имя Мирослава: история и значение'): ").strip()
        if topic:
            generate_article(topic)
        else:
            print("Тема не введена.")
    elif choice == "2":
        print("До встречи! 🌿")
    else:
        print("Неверный выбор.")

if __name__ == "__main__":
    main()