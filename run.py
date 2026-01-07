# Input from user
marital_status = input("Enter marital status (M for Married, U for Unmarried): ").upper()
gender = input("Enter gender (M for Male, F for Female): ").upper()
age = int(input("Enter age: "))

# Insurance decision
if marital_status == 'M':
    print("Driver is insured.")
elif marital_status == 'U' and gender == 'M' and age > 30:
    print("Driver is insured.")
elif marital_status == 'U' and gender == 'F' and age > 25:
    print("Driver is insured.")
else:
    print("Driver is not insured.")
