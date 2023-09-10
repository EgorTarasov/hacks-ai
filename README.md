# Установка

<!-- add requirements to readme -->

## Подготовка окружкния

данное рещение использует python 3.10

### linux (ubuntu):

```bash
python3 -m venv venv
source venv/bin/activate
```

### Установка зависимостей

для работы с аудио необходимо установить ffmpeg и PortAudio

macos (homebrew):

```bash
    brew install ffmpeg portaudio
```

linux (apt):

```bash
    sudo apt install ffmpeg portaudio
```

```bash
    pip3 install -r requirements.txt
```

## Запуск

для запуска бота необходимо запустить main.py

```bash
python3 main.py
```

для запуска api необходимо запустить api.py

```bash
python3 api.py
```


## Архитектура решения
1) Для каждой серии локомотива генерируем свою базу эмбеддингов для неисправностей с помощью ranking модели (distilbert-multilingual-nli-stsb-quora-ranking). 
2) Входящее аудио преобразуем в текст с помощью whisper
3) Преобразуем текст в эмбеддинг с помощью ranking модели
4) Ищем ближайшие эмбеддинги в базе конкретного локомотива.
5) Получем решение для неисправности и сопутствующую информацию.
6) Преобразуем ответ в читабельный вид

## Валидация
Поскольку наша модель использует всю документацию для полного покрытия возможных неисправностей, нам было необходимо построить правильную валидацю.
Для этого мы перефразируем неисправности с помощью генеративной модели, чтобы качественно проверить матчинг вопроса и проблемы.  
Для тестирования speech2text были записаны с указанием неисправности  
```bash
python3 validate.py
```
