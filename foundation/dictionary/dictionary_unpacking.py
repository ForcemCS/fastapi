car_data = {
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2021
}

class Car:
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year

# 使用关键字参数创建实例
# my_car = Car(brand="Toyota", model="Corolla", year=2021)
my_car = Car(**car_data)          #使用字典解包，上边效果一致

print(my_car.brand)