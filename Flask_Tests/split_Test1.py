s = [["123456789011223344556677889900123fdlgsfdl"], ["01234567899876543210"], ["dlakhjflkahdf"]]
acc_Id = "9876543210"
foundTables = []
i = 0

for item in s:
    split_List = [item[0][i:i+10] for i in range(0, len(item[0]), 10)]

    for ID in split_List:
        if ID == acc_Id:
            print("Chat Found: " + item[0])

for item in s:
    if item[0][0:10] == acc_Id:
        foundTables.append([item[0], item[0][10:20]])
    elif item[0][10:20] == acc_Id:
        foundTables.append([item[0], item[0][0:10]])

print(foundTables)
