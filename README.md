# About
Тестовый проект, в котором GPT выполняет роль ассистента, способного забронировать отель
Модель работает на английском языке.

# Demo
[Google Colab](https://colab.research.google.com/drive/1dgFhlSbSAHsxxX6Api24uohhq30kfKpG?usp=sharing)

# Основная идея
Бронирование происходит в несколько шагов: 
1. Пользователь вводит параметры отеля в свободной форме, например "Find a hotel in Moscow for the next week"
2. LLM генерирует json blob следующего вида:
```json
{
    "name": "search_hotels_tool",
    "arguments": {
        "location": "Moscow",
        "checkin_date": null,
        "checkout_date": null,
        "adults_number": null,
        "order_by": "popularity"
    }
}
```

3. По отсутствующим в запросе пользователя параметрам (здесь это checkin_date, checkout_date, adults_number) пользователю указывается какую информацию нужно указать в запросе:

```Can you provide me with the missing booking parameters: checkin_date, checkout_date, adults_number?```

4. Пользователь дописывает запрос, пока не будут указаны все нужные параметры. Если указано все что требуется, модель успешно вызовет search_hotels_tool, который вернет например:
```
Here are the hotels:
id: 1
name: Hotel A
location: Moscow
rating: 4.5
price: 200
class: 8.5
address: Address A

id: 2
name: Hotel B
location: Moscow
rating: 4.0
price: 150
class: 6.0
address: Address B

id: 3
name: Hotel C
location: Moscow
rating: 3.5
price: 100
class: 4.0
address: Address C
```
5. Пользователь в свободной форме выбирает отель, например: ```"I like Hotel A"```
6. LLM вызывает инструмент для бронирования:
```json
{
    "name": "book_hotel_tool",
    "arguments": {
        "id": 1
    }
}
```
Код для инференса модели в main.py.

# Используемая модель и данные
Модель (в данном случае qwen 7b) была дообучена на синтетических данных.

Код для генерации данных в файле generate_dataset.ipynb, в нем используются несколько open source моделей (qwen 7b и qwen 72b) для генерации вариантов ответа, а модель-судья (qwen 72b) выбирает и по необходимости дополняет лучший вариант.

Возможные вопросы пользователя создаются через 7b и 72b модели. (в итоговых датасетах train/val.data некоторые запросы написаны не полностью, ожидается что модель должна корректно работать в таких ситуациях).

# Дообучение
Код для дообучения qwen 7b в файле train.ipynb.

# Оценка модели
В eval.ipynb модели qwen 7b и qwen-7b-finetuned проверяются по метрикам:
- Rouge
- Bleu
- Precision по аргументам json blob
- Количество ошибок при парсинга json и их отношение к общему кол-ву генераций

| Метрика | Qwen 7b | Qwen 7b finetuned |
|---|---|---|
| Precision по аргументам json blob | 0.69 | 0.51 |
| Количество ошибок парсинга json | 5 | 1 |
| Отношение ошибок к общему числу генераций | 0.04 | 0.01 |

В целом можно сказать, что обученная модель реже генерирует лишние аргументы в своем json ответе и чаще правильно парсит их из запроса пользователя.
