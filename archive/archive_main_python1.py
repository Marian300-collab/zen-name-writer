import os
import requests
import json
import random
from datetime import datetime

# Настройки для локальной модели
MODEL_NAME = "qwen2.5:14b" 
OLLAMA_URL = "http://localhost:11434/api/generate"

# ==========================================
# НОВЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С ШАБЛОНАМИ
# ==========================================

def load_list(file_path):
    """Загружает список элементов из файла templates/, игнорируя заголовки"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Убираем пустые строки и строки, начинающиеся с # (заголовки markdown)
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
    # Берем 3-4 случайные сенсорные детали
    sensory_sample = random.sample(sensory, min(4, len(sensory))) if sensory else []
    scholar = random.choice(scholars) if scholars else "Анна Суперанская — словари имён"
    ending = random.choice(endings) if endings else "Закрыла тетрадь и убрала на полку"
    
    return {
        "anchor": anchor,
        "sensory": sensory_sample,
        "scholar": scholar,
        "ending": ending
    }

# Системный промпт v6.0 — исправленный и очищенный
SYSTEM_PROMPT = """
Ты — автор Дзен-канала «О чём говорят Славянские Веды». Не этнограф в поле, не мистик, не ностальгирующий старик. Ты — наблюдатель, который соединяет три пласта памяти: славянский быт, советское детство и современную жизнь. Ты замечаешь, как в имени ребёнка, в бабушкиной вышивке, в песне из советского фильма, в запахе прелой листвы или в скрипе половицы живёт одна и та же практическая мудрость. Твоя задача — написать статью, которая не просто информирует, а создаёт эмоциональную связь, удерживает внимание до конца и провоцирует обсуждение имен в комментариях. Ты пишешь душевные, личные истории про имена с глубоким смыслом.

Ключевая философия: Магия предков — и славянских, и советских — это не сказка и не эзотерика. Это передовая для своего времени физика, биология, психология, педагогика, которую они описывали через наречение, метафоры, обряды, песни, сказки, а позже — через пионерские костры, дачные разговоры на кухне, заводские клубы и дворовые игры.

Главный принцип: Мы пишем только о том, что можно потрогать, прочитать или вспомнить: берестяные грамоты, музейные экспонаты, диалектные слова, живая память бабушек, советские учебники, дворовые считалки, песни из кино, имена, которые носили деды. Мы не гадаем по камням и не пишем о «древних атлантах».

ВАЖНО: Все статьи этого канала — ТОЛЬКО ПРО ИМЕНА. В заголовке всегда должно быть слово "Имя" или "Имена".

## РАНДОМИЗАЦИЯ (КРИТИЧЕСКИ ВАЖНО ПРОТИВ ШАБЛОННОСТИ)
Перед написанием каждой статьи выбери случайные параметры. Никогда не используй одну и ту же комбинацию дважды.
1. Точка входа: диалог / сенсорная деталь / вопрос / находка / действие / контраст "раньше/сейчас".
2. Голос рассказчика: Бабушка 60-70 лет / Мама 35-45 лет / Молодая мама 25-30 лет / Наблюдатель со стороны.
3. Доминирующее чувство: Обоняние / Слух / Осязание / Зрение.
4. Структурный приём: Классические 5 блоков / Начать с конца (flashback) / Письмо / Диалог / Наблюдение за другим.

СТРАТЕГИЯ КАРТОЧКИ ПУБЛИКАЦИИ (CTR)
Заголовок (H1): 60–80 символов. Понятный, без восклицательных знаков, без слов «шок», «секрет», «топ». Всегда содержит слово "Имя" или "Имена".
Подводка (Лид): 1–2 предложения (15–40 слов). Не дублирует заголовок, создаёт атмосферу или бытовой конфликт.

НАУЧНАЯ БАЗА И ДОСТОВЕРНОСТЬ
Опирайся на труды: Анна Суперанская, Николай Петровский, Владимир Никонов, Макс Фасмер, Дмитрий Зеленин, Владимир Пропп, Валерий Мокиенко, Владимир Даль, Андрей Зализняк.

НАРРАТИВНЫЙ ШАБЛОН (ОБЯЗАТЕЛЬНАЯ СТРУКТУРА)
Пиши строго от первого лица. Абзацы не длиннее 3–4 строк.
БЛОК 1. БЫТОВОЙ ТРИГГЕР (3–4 абзаца): Узнаваемая ситуация, спор об имени, неловкость.
БЛОК 2. ВНУТРЕННЕЕ НАПРЯЖЕНИЕ (3–4 абзаца): Пауза, сомнение, личное воспоминание с сенсорикой (деревня, советская квартира, пионерлагерь, двор).
БЛОК 3. ТОЧКА ОЗАРЕНИЯ (2–3 абзаца): Момент понимания через чужую фразу или действие. Скрытое разведение понятий через нарратив (не списком!).
БЛОК 4. ТРАНСФОРМАЦИЯ ЧЕРЕЗ ДЕЙСТВИЕ (2–3 абзаца): Конкретные действия. Метод четырёх слоёв: корень и смысл, звучание, 4-5 ласкательных форм, 3-4 примера с отчествами.
БЛОК 5. ФИЛОСОФСКОЕ ОБОБЩЕНИЕ (2–3 абзаца): Связь с универсальными ценностями. Этимология или фразеологизм органично в конце блока.

СТИЛЬ И ТЕХНИКА
Конкретика и сенсорика (минимум 3 детали на сцену). Чередование коротких и длинных предложений. Тёплый, доверительный тон, как разговор на кухне.

БЛОК ПРО СССР
Всегда в положительном, тёплом ключе, как продолжение народной традиции. Без клише «совок» или «дефицит».

❌ ЗАПРЕТЫ И ТАБУ
Эзотерика: «энергия», «вибрации», «карма», «родовые программы», «Явь/Навь», «места силы».
Конспирология: «атланты», «гипербореи», «тайный орден».
Клише: «как корабль назовёшь», «имя — это судьба», «связь поколений».
Категоричность и пустые метафоры: «душа поёт», «предки завещали».
Разведение понятий списком: «Обряд — это..., Примета — это...».
Явные алгоритмы: «Шаг 1...», «Во-первых...», «Итак, мы видим...».
Прямые призывы к действию: "подпишитесь", "ставьте лайк", "пишите в комментариях" (Дзен пессимизирует это).

✅ ФИНАЛ И ВОВЛЕЧЕНИЕ (ER)
В самом конце задай ОДИН конкретный, открытый вопрос, вытекающий из темы. 
Формат финала: Только вопрос (8-15 слов). Без фраз "поделитесь в комментариях" или "подписывайтесь". Без эмодзи в самом конце.

ОБЪЁМ И СТРУКТУРА
4000–6000 знаков. Абзацы не длиннее 3–4 строк. Подзаголовки H2 каждые 2–3 смысловых блока.

ИНСТРУКЦИЯ ДЛЯ ИИ
1. Проанализируй тему.
2. Напиши короткий план для себя (Точка входа, Голос, Чувство, Приём).
3. Предложи 3 варианта заголовков и подводок.
4. Напиши полный текст статьи по шаблону.
5. Предложи 3 варианта финального вопроса.
"""

def generate_article(topic):
    print(f"\n⏳ Генерирую статью на тему: 'Имя {topic}'... (это может занять 2-3 минуты)")
    
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nТема статьи: Имя {topic}\nКлючевой бытовой предмет или ситуация: [выбери сам на основе темы]\nГлавный инсайт (озарение): [выбери сам на основе темы]\n\nНапиши полную статью, строго следуя всем инструкциям выше.",
        "stream": False
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
        return article_text
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка: Не удалось подключиться к Ollama. Убедись, что программа Ollama запущена.")
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
        print("❌ Ошибка: Не найден файл промпта редактора (04_editor.md).")
        return

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{editor_prompt}\n\nВот текст черновика для анализа и редактирования:\n\n{article_text}",
        "stream": False
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
        print("\n" + "="*50)
        print(edit_report)
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка: Не удалось подключиться к Ollama.")
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
            print(f"✅ Загружен промпт: {path}")
            break
            
    if not rewriter_prompt:
        print("❌ Ошибка: Не найден файл 08_rewriter.md или 08_rewriter_simple.md")
        return

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{rewriter_prompt}\n\nВот черновик для переписывания:\n\n{article_text}",
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        rewritten_text = result.get("response", "")
        
        if not rewritten_text or len(rewritten_text.strip()) < 100:
            print("❌ Ошибка: Модель вернула пустой или слишком короткий ответ!")
            print(f"Длина ответа: {len(rewritten_text)} символов")
            return
        
        os.makedirs("output", exist_ok=True)
        new_filename = f"output/rewritten_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(new_filename, "w", encoding="utf-8") as f:
            f.write(rewritten_text)
        
        print(f"\n✅ Переписанная статья сохранена: {new_filename}")
        print(f"Длина: {len(rewritten_text)} символов")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка подключения к Ollama.")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


def run_pipeline(topic):
    print(f"\n⏳ Запускаю Оркестратор для темы: 'Имя {topic}'... (это займёт 3-5 минут)")
    
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
        "prompt": f"{pipeline_prompt}\n\nВходные данные:\nТема: Имя {topic}\nОбъём: 5000 знаков\nУже использованные темы: нет\n\nСгенерируй полный пакет.",
        "stream": False
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
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка: Не удалось подключиться к Ollama.")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")


def generate_gold_v2(topic):
    print(f"\n⏳ Генерирую длинную статью по Золотому стандарту v2: 'Имя {topic}'... (это займёт 3-5 минут)")
    
    # 1. Загружаем основной промпт
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

    # 2. Загружаем эталонный пример (few-shot)
    few_shot_example = ""
    try:
        with open("best_examples/05_full_articles.md", "r", encoding="utf-8") as f:
            few_shot_example = f.read()
    except FileNotFoundError:
        print("⚠️ Не найден best_examples/05_full_articles.md, генерирую без эталона.")

    # 3. Собираем уникальную комбинацию
    combo = build_unique_combination()

    # 4. Спрашиваем пользователя, но даём возможность использовать случайные значения
    print(f"\n💡 Система подобрала случайный предмет-якорь: '{combo['anchor']}'")
    user_anchor = input("Введи свой предмет-якорь (или нажми Enter, чтобы использовать случайный): ").strip()
    anchor = user_anchor if user_anchor else combo['anchor']
    
    user_insight = input("Введи ключевой инсайт (или нажми Enter для стандартного): ").strip()
    insight = user_insight if user_insight else "имя — это не выбор, а продолжение рода"

    # 5. Спрашиваем семейную структуру
    print("\n👨‍👩👧 Введи семейную структуру (формат: Имя, родство к рассказчику)")
    print("Пример: Кирилл, отец; Кирилл, сын; Аня, внучка")
    family_input = input("Или нажми Enter для стандартной семьи: ").strip()
    
    if not family_input:
        family_input = "Кирилл, отец; Кирилл, сын; Аня, внучка"
    
    # 6. Формируем финальный промпт
    final_prompt = f"""{gold_prompt}

# 👨‍👩‍👧 СЕМЕЙНАЯ СТРУКТУРА (АБСОЛЮТНЫЙ ЗАПРЕТ НА ГАЛЛЮЦИНАЦИИ!)
В статье могут быть ТОЛЬКО эти персонажи:
{family_input}

ПРАВИЛА:
- НЕ выдумывай других родственников (мужей, братьев, правнуков).
- НЕ меняй пол и роли (сын не может быть беременным, внучка не может быть взрослой).
- НЕ дублируй предметы (если мишка у внучки, его нет у бабушки).

# 📚 ЭТАЛОННЫЙ ПРИМЕР (учит СТИЛЮ, не копируй дословно!)
{few_shot_example}

# 🎲 УНИКАЛЬНАЯ КОМБИНАЦИЯ ДЛЯ ЭТОЙ СТАТЬИ:
**Предмет-якорь:** {anchor}
**Сенсорные детали (используй 3-4 из этого списка):**
{chr(10).join('- ' + s for s in combo['sensory'])}
**Учёный/Действие:** {combo['scholar']}
**Финал:** {combo['ending']}

# 🎯 ТВОЯ ЗАДАЧА:
Напиши УНИКАЛЬНУЮ статью по входным данным:
- Тема (Имя): {topic}
- Предмет-якорь: {anchor}
- Ключевой инсайт: {insight}

Используй элементы из "Уникальной комбинации", но создавай НОВЫЕ диалоги, ситуации и детали. НЕ копируй эталонный пример — он показывает только стиль и структуру.
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": final_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        article_text = result.get("response", "")
        
        if not article_text or len(article_text.strip()) < 100:
            print("❌ Ошибка: Модель вернула пустой ответ!")
            print(f"Длина ответа: {len(article_text)} символов")
            return
        
        os.makedirs("output", exist_ok=True)
        # Делаем имя файла более читаемым
        filename = f"output/gold_v2_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(article_text)
        
        print(f"\n✅ Статья сохранена: {filename}")
        print(f"Длина: {len(article_text)} символов")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка подключения к Ollama.")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


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
            print(f"✅ Загружен промпт: {path}")
            break
            
    if not photo_prompt:
        print("❌ Ошибка: Не найден файл 07_photo_director.md")
        return

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{photo_prompt}\n\nВот текст статьи для анализа:\n\n{article_text}",
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        photo_text = result.get("response", "")
        
        if not photo_text or len(photo_text.strip()) < 100:
            print("❌ Ошибка: Модель вернула пустой ответ!")
            print(f"Длина ответа: {len(photo_text)} символов")
            return
        
        os.makedirs("output", exist_ok=True)
        new_filename = f"output/photo_prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(new_filename, "w", encoding="utf-8") as f:
            f.write(photo_text)
        
        print(f"\n✅ Промты для фото сохранены: {new_filename}")
        print(f"Длина: {len(photo_text)} символов")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка подключения к Ollama.")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


def main():
    while True:
        print("\n" + "="*50)
        print("🌿 ZenName Writer: Редакция ИИ-агентов")
        print("="*50)
        print("1. Сгенерировать статью (Быстрый режим, Автор)")
        print("2. Запустить полный пайплайн (Оркестратор: Статья + SEO + Фото)")
        print("3. Отредактировать готовую статью (Редактор)")
        print("4. Переписать статью в живом стиле (Трансформер)")
        print("5. Золотой стандарт v2 (Длинная статья с уникальными комбинациями)")
        print("6. Сгенерировать промты для фото (Фото-директор)")
        print("7. Выход")
        
        choice = input("\nВыбери действие (1, 2, 3, 4, 5, 6 или 7): ").strip()
        
        if choice == "1":
            topic = input("Введи имя для статьи (например, 'Мирослава'): ").strip()
            if topic:
                generate_article(topic)
        elif choice == "2":
            topic = input("Введи имя для полного пайплайна (например, 'Мирослава'): ").strip()
            if topic:
                run_pipeline(topic)
        elif choice == "3":
            filename = input("Введи имя файла для редактирования (например, 'output/article_...md'): ").strip()
            if filename and os.path.exists(filename):
                edit_article(filename)
            else:
                print("❌ Файл не найден. Проверь имя и путь.")
        elif choice == "4":
            filename = input("Введи имя файла для переписывания (например, 'output/pipeline_...md'): ").strip()
            if filename and os.path.exists(filename):
                rewrite_article(filename)
            else:
                print("❌ Файл не найден. Проверь имя и путь.")
        elif choice == "5":
            topic = input("Введи имя для статьи (например, 'Мирослава'): ").strip()
            if topic:
                generate_gold_v2(topic)
            else:
                print("❌ Имя не введено.")
        elif choice == "6":
            filename = input("Введи имя файла статьи (например, 'output/gold_v2_...md'): ").strip()
            if filename and os.path.exists(filename):
                generate_photo_prompts(filename)
            else:
                print("❌ Файл не найден. Проверь имя и путь.")
        elif choice == "7":
            print("До встречи! 🌿")
            break
        else:
            print("❌ Неверный выбор. Попробуй снова.")


if __name__ == "__main__":
    main()