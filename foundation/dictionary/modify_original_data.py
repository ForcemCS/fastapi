# 1. 我们的原始数据列表，包含两个字典
my_list = [
    {'name': 'Alice', 'city': 'New York'},
    {'name': 'Bob', 'city': 'London'}
]

# 2. 我们创建一个新变量，让它引用列表中的第一个字典
person_to_change = my_list[0]

# 3. 我们通过这个新的引用来修改字典
print(f"修改前 'person_to_change': {person_to_change}")
person_to_change['city'] = 'Paris'  # 修改城市
print(f"修改后 'person_to_change': {person_to_change}")

# 4. 现在，我们来检查原始的 my_list。你会发现它也被改变了！
print("\n检查原始列表 my_list:")
print(my_list)