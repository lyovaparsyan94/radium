# Проект Асинхронное Скачивание

## Краткие ответы на вопросы:

### Как вы реализовали асинхронное выполнение задач в вашем скрипте?

Я использовал библиотеку asyncio для создания и выполнения асинхронных задач. Основная функция main запускает
асинхронные задачи с помощью asyncio.gather, что позволяет выполнять несколько задач параллельно.

### Какие библиотеки использовались для скачивания содержимого репозитория и для каких целей?

Я использовал aiohttp для асинхронного скачивания файлов с URL. Для работы с файлами использовалась библиотека aiofiles,
которая позволяет асинхронно читать и записывать файлы.

### Какие проблемы асинхронности вы сталкивались при выполнении задания и как их решали?

Одна из проблем заключалась в корректной обработке ошибок HTTP-запросов. Для этого использовалась обработка исключений
aiohttp.ClientResponseError и моки (mocks) для имитации ответов сервера с ошибками.

### Как вы организовали скачивание файлов во временную папку?

Я создал временную директорию с помощью tempfile.TemporaryDirectory, куда скачиваются файлы. Путь к этой директории
задавался с помощью Path.resolve, и файлы сохранялись в эту директорию.

### Какие основные требования wemake-python-styleguide вы находите наиболее важными для поддержания качества кода?

Важные требования включают ограничение длины строки (80 символов), строгое соблюдение PEP8, использование аннотаций
типов и явное объявление всех переменных. Это помогает поддерживать читаемость и качество кода.

### Как вы настраивали свой проект для соответствия конфигурации nitpick, указанной в задании? Были ли трудности при настройке?

Я создал и настроил файл .nitpick-style.toml согласно требованиям, а также использовал команду nitpick fix для
приведения кода в соответствие с конфигурацией. Основной трудностью было правильное подключение всех необходимых стилей
и проверка конфигурации.

### Какие инструменты использовали для измерения 100% покрытия тестами?

Для измерения покрытия тестами использовался pytest с плагином pytest-cov, который позволяет генерировать отчет о
покрытии кода тестами.

### Какие типы тестов вы написали для проверки функциональности вашего скрипта? (Например, модульные тесты, интеграционные тесты)

Я написал модульные тесты для проверки отдельных функций, таких как calculate_sha256, download_file, и интеграционные
тесты для проверки всей цепочки выполнения задач через функцию main.

### Как вы тестировали асинхронный код? Использовали ли вы моки (mocks) или стабы (stubs) для тестирования асинхронных операций?

Для тестирования асинхронного кода я использовал библиотеку pytest с плагином pytest-asyncio. Моки (mocks) и стабы (
stubs) использовались для имитации HTTP-запросов и обработки ошибок, что позволило проверить корректное выполнение
асинхронных операций.

## Установка зависимостей

    poetry install

## Для запуска тестов используйте команду:

    pytest --cov=src --cov-report=term-missing

## Для генерации HTML-отчета используйте:

    coverage html

