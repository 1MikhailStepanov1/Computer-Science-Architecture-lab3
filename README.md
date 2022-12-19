# Computer Science Architecture Lab 3

Степанов Михаил Андреевич P33312

## Вариант

'alg | risc | harv | hw | instr | struct | stream | port | prob5'

* 'alg' - java/javascript подобный язык
* 'risc' - система команд должна быть упрощенной, в духе RISC архитектур
* 'harv' - Гарвардская архитектура
* 'hw' - Control Unit реализован как часть модели, микрокода нет
* 'instr' - каждая инструкиция расписана по-тактово, но в журнале фиксируется только результат выполнения
* 'struct' - в виде высокоуровневой структуры данных. Одна инструкция укладывается в одно машинное слово
* 'stream' - ввод-вывод осуществляется как поток токенов
* 'port' - port-mapped
* 'prob5' - Project Euler. Problem 5

## Язык

* Объявление переменных через ключвое слово 'let'
* Доступен цикл 'while'
* Доступна функция ввода 'input()' и функция вывода 'print()'
* Доступна инструкция ветвления 'if'
* Разрешенные математические операции:
  * '+' бинарный плюс
  * '-' бинарный минус
  * '=' присваивание
  * '*' умножение
  * '%' остаток от деленмия

##BNF

#### `<program> ::= <term>`
#### `<name> ::= [a-zA-Z]+`
#### `<term> ::= <variable initialization> | <while cycle> | <print function> | <term> <term>`
#### `<value> ::= <number> | <string>`
#### `<number> ::= javascript number`
#### `<value> ::= javascript string`
#### `<variable initialization> ::= let <name> = <value>`
#### `<operation> ::= + | - | * | % | > | <`
#### `<print> ::= print(<value>)`
#### `<input> ::= input(<value>)`