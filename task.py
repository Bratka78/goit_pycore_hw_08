from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
   pass

class Phone(Field):
    def __init__(self, value):
        if not self.valid_numer(value):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

    def valid_numer(self, value):
        return value.isdigit() and len(value) == 10   
    
class Birthday(Field):
    def __init__(self, value):
        try:
            # Перевіряємо формат і перетворюємо рядок на datetime об'єкт
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
            
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

#Логіка

class Record():
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None # Початково дня народження немає

    # реалізація класу
    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        if not phone:
            raise ValueError(f"Phone {old_number} not found.")
        new_phone = Phone(new_number)
        self.remove_phone(old_number)
        self.phones.append(new_phone)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
    
    def add_birthday(self, birthday_string):
        self.birthday = Birthday(birthday_string)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        phones_str = "; ".join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
        
    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()
        
        for record in self.data.values():
            if not record.birthday:
                continue
                
            # Беремо дату народження в цьому році
            bday = record.birthday.value.replace(year=today.year)
            
            # Якщо день народження вже пройшов у цьому році, дивимось на наступний
            if bday < today:
                bday = bday.replace(year=today.year + 1)
            
            if 0 <= (bday - today).days <= 7:
                congratulation_date = bday
                if congratulation_date.weekday() == 5:  # Субота -> Понеділок
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:  # Неділя -> Понеділок
                    congratulation_date += timedelta(days=1)
                
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })
        return upcoming_birthdays

# Хендлери

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter user name and the required argument."
        except KeyError:
            return "Contact not found."
    return inner

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    return "Contact not found."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return "; ".join(p.value for p in record.phones)
    return "Contact not found."

@input_error
def add_birthday(args, book):
    name, date = args
    record = book.find(name)
    if record:
        record.add_birthday(date)
        return "Birthday added."
    return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday}"
    return "Birthday not found or contact doesn't exist."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join([f"{item['name']}: {item['congratulation_date']}" for item in upcoming])

#Основна частина

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Якщо файлу немає, створюємо порожню книгу
    
def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input: continue
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            if not book.data:
                print("Address book is empty.")
            for record in book.data.values():
                print(record)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()