Домашнє завдання №13
Перша частина

У цьому домашньому завданні ми продовжуємо доопрацьовувати застосунок REST API із домашнього завдання 12.
Завдання

    [*] Реалізуйте механізм верифікації електронної пошти зареєстрованого користувача;
    [*] Обмежуйте кількість запитів до своїх маршрутів контактів. Обов’язково обмежте швидкість створення контактів для користувача;
    [*] Увімкніть CORS для свого REST API;
    [*] Реалізуйте можливість оновлення аватара користувача. Використовуйте сервіс Cloudinary;

Загальні вимоги

    [*] Усі змінні середовища повинні зберігатися у файлі .env. Всередині коду не повинно бути конфіденційних даних у «чистому» вигляді;
    [*] Для запуску всіх сервісів і баз даних у застосунку використовується Docker Compose;

Додаткове завдання

    [*] Реалізуйте механізм кешування за допомогою бази даних Redis. Виконайте кешування поточного користувача під час авторизації;
    [] Реалізуйте механізм скидання паролю для застосунку REST API;

Друга частина

У цьому домашньому завданні необхідно доопрацювати застосунок Django із домашнього завдання 10.
Завдання

    Реалізуйте механізм скидання паролю для зареєстрованого користувача;
    Усі змінні середовища повинні зберігатися у файлі .env та використовуватися у файлі settings.py;


Мехінзм скидання паролю

    - Користувач запитує скидання пароля, вказуючи свою адресу електронної пошти у формі скидання пароля.
    - Django генерує унікальний токен скидання пароля і надсилає лист із посиланням на скидання пароля на адресу електронної пошти користувача. Посилання вмикає маркер скидання пароля як параметр.
    - Коли користувач натискає на посилання скидання пароля, Django перевіряє маркер скидання пароля, і з’являється форма для введення нового пароля.
    - Користувач вводить новий пароль та надсилає форму.
    - Django оновлює пароль користувача та повідомляє про це користувача.