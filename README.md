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

## Язык программирования

Использована упрощенная версия языка JavaScript
Типизация: статическая сильная неявная

* Объявление переменных через ключевое слово `let`
* Доступен цикл `while`
* Доступна функция ввода `input()` и функция вывода `print()`
* Доступна инструкция ветвления `if`
* Разрешенные математические операции:
  * `+` - бинарный плюс
  * `-` -  бинарный минус
  * `=` - присваивание
  * `*` - умножение
  * `%` - остаток от деления

### BNF

#### `<program> ::= (<source element>)+`
#### `<source element> ::= <statement>`
#### `<statement> ::= <allocation statement> | <assignment statement> | <if statement> | <iteration statement> | <read statement> | <print statement>`
#### `<allocation statement> ::= "let" <name> "=" <number> | <row> ";"`
#### `<assignment statement> ::= <name> "=" <number> | <name> | <expression> ";"`
#### `<if statement> ::= "if" (<name> | <expression> | <number>) <comparison sign> (<name> | <expression> | <number>) "\n{" (<statement>)+ "}"`
#### `<iteration statement> ::= "while" (<name> | <expression> | <number>) <comparison sign> (<name> | <expression> | <number>) "\n{" (<statement>)+ "}"`
#### `<read statement> ::= "input(" <name> ");"`
#### `<print statement> ::= "print( <name> ");"`
#### `<expression> ::= (<name> | <number>) <operation sign> (<name> | <number>)`
#### `<comparison sign> ::= "!=" | "==" | ">" | "<" | "<=" | ">="`
#### `<name> ::= [a-zA-Z]+`
#### `<number> ::= [0-9]+`
#### `<row> ::= "[a-zA-Z]*"`
#### `<operation sign> ::= "+" | "-" | "/" | "%" | "*"`

### Пример
```javascript
let n = 2520;
let i = 20;
while (i > 0)
{
if (n % i == 0)
{
i = i - 1;
}
else
{
n = n + 2520;
i = 20;
}
if (i == 1)
{
print(n);
}
}
```

```javascript
let temp = "hello, world";
print(temp);
```

## Система команд


| ФИО          | алг.  | LoC | code байт | code инстр. | инстр.   | такт.    | вариант                                                          |
|--------------|-------|-----|-----------|-------------|----------|----------|------------------------------------------------------------------|
| Степанов М.А | hello | 2   | -         | -           | 60       | 204      | `alg - risc - harv- hw - instr - struct - stream - port - prob5` | 
| Степанов М.А | cat   | 7   | -         | -           | 67       | 251      | `alg - risc - harv- hw - instr - struct - stream - port - prob5` |
| Степанов М.А | prob5 | 18  | -         | -           | 5065440  | 19090394 | `alg - risc - harv- hw - instr - struct - stream - port - prob5` |
