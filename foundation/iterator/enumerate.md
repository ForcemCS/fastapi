### enumerate使用方法

在 Python 中，`enumerate()` 是一个非常常用的内置函数，主要用于在 遍历可迭代对象（如列表、元组、字符串等）时，同时获取元素的索引（**可以自定义**）和对应的值。

### 🔹 基本语法

```
enumerate(iterable, start=0)
```

- `iterable`：可迭代对象，比如 `list`、`tuple`、`str` 等。
- `start`：可选参数，表示索引起始值，默认从 `0` 开始。

### 🔸 常见用法示例

#### ✅ 示例 1：遍历列表并带上索引

```
fruits = ['apple', 'banana', 'cherry']

for index, fruit in enumerate(fruits):
    print(index, fruit)
    
## 输出
0 apple
1 banana
2 cherry
```

#### ✅ 示例 2：自定义起始索引

```
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")
##输出
1. apple
2. banana
3. cherry
```

#### ✅ 示例 3：与 `list()` 结合使用

```
print(list(enumerate(fruits)))
## 输出
[(0, 'apple'), (1, 'banana'), (2, 'cherry')]
```