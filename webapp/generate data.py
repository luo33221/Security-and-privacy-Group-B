import csv
from faker import Faker
import random

fake = Faker()

def generate_fake_row():
    patientname = fake.name()
    age = random.randint(18, 90)
    gender = random.choice(['Male', 'Female'])
    doctor = fake.name()
    illness = fake.word()
    diagnosis = fake.word()
    return [patientname, age, gender, doctor, illness, diagnosis]

def generate_fake_csv(file_path, num_rows):
    with open(file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['patientname', 'age', 'gender', 'doctor', 'illness', 'diagnosis'])
        for _ in range(num_rows):
            row = generate_fake_row()
            csv_writer.writerow(row)

csv_file_path = "fake_data.csv"
num_rows = 100  
generate_fake_csv(csv_file_path, num_rows)
print(f"CSV file generated: {csv_file_path}")
