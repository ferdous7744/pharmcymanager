from random import choice


#هدي تعريف تع ليست تع دواوات
class ListNode:
    def __init__(self, name,amount):
        self.name = name
        self.amount = amount
        self.next = None

    def Print(self):
        print(f"name = {self.name} | amount = {self.amount}  \n",)
        if self.next is not None:
            self.next.Print()
#تحويل النص إلى Linked List
def buildList(text):
    if isinstance(text, ListNode):
        return text

    if text == "NULL":
        return None

    items = text.split("|")

    name, qty = items[0].split(":")
    head = ListNode(name, int(qty))
    current = head

    for item in items[1:]:
        name, qty = item.split(":")
        current.next = ListNode(name, int(qty))
        current = current.next

    return head
#قراءة الملف وبناء الشجرة
def BuildTree(filename):
    root = None

    with open(filename, "r") as f:
        for line in f:
            id, name, price, category, product_text = line.strip().split(",")

            node = Node(int(id), name, float(price), category, product_text)

            root = insert(root, node)

    return root
#تحويل Linked List إلى نص
def listToText(head):
    if head is None:
        return "NULL"

    items = []
    while head:
        items.append(f"{head.name}:{head.amount}")
        head = head.next

    return "|".join(items)
#حفظ الشجرة
def saveTree(root, fileName):
    if root is None:
        return

    saveTree(root.left, fileName)

    products = listToText(root.product)
    file = open(fileName, "a")

    file.write(f"{root.id},{root.name}, {root.price} ,{root.category}, {products}\n")

    saveTree(root.right, fileName)
#هدي تخدملك ليست تع مكونات تمدلها ايدونتيفاي تع دوا
def makeList (drug):
    p=input(f"give Product 1 of drug{drug} ")
    A=float( input(f"give amount 1 of drug{drug} "))

    First=ListNode(p,A)
    head=First
    check=True
    i=2
    while check :
        p= input(f"give product's name {i}  of drug {drug}")
        A= float( input(f"give product's amount {i} of drug {drug}"))
        current =ListNode(p,A)
        First.next=current
        i+=1
        First = current
        checkmsg = input("add other ? y/n")
        if checkmsg== "n" :
            check= False
    return head
def findMin(root):
    while root.left != None:
        root=root.left
    return root
def deletProduct(root, id, name):


    while root is not None and root.id != id:
        if id > root.id:
            root = root.right
        else:
            root = root.left

    if root is None:
        print("ID not found in tree")
        return False


    if root.product is None:
        print("No products in this node")
        return False


    current = root.product
    before = None

    while current is not None and current.name != name:
        before = current
        current = current.next

    if current is None:
        print("the product is unfounded !")
        return False


    if before is None:
        root.product = current.next
    else:
        before.next = current.next

    print("the deletion done !!")
    return True
#------------------------ تعريف الشجرة -----------
class Node:
    def __init__(self, id , name , price , category , product , left=None, right=None):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.product=buildList(product)
        self.left = left
        self.right = right
    def display(self):
        print(f"drug id : {self.id } > drug name : {self.name} > price : {self.price} > category : {self.category} \n")
# بالترتيب
def inOrder(node):
    if node is None:
        return

    inOrder(node.left)

    print("DRUG:")
    node.display()

    print("PRODUCTS:")
    if node.product is not None:
        node.product.Print()
    else:
        print("No products")

    print("\n" + "-"*30)

    inOrder(node.right)

def insert(root, node):
    if root is None:
        return node

    if node.id < root.id:
        root.left = insert(root.left, node)
    else:
        root.right = insert(root.right, node)

    return root
def addNode(root):
    print("hello in building tree panel !! ")
    ID = int(input("insert your drug Id : "))
    NAME = input("insert your drug Name : ")
    PRICE = float(input("insert your drug price: "))
    CATG = input("insert your drug category : ")
    PRODUCT = makeList(ID)
    New = Node(ID, NAME, PRICE, CATG, PRODUCT)
    head = insert(root, New)
    return head
def search(id,Root):
    if Root.id == id:
        Root.display()
        return True
    elif Root.right==None and Root.right == None :
        if Root.id == id :
            return True
        else:
            print("the drug is executed !! ")
            return False

    else:
        if id> Root.id:
           return search(id,Root.right)
        else:
           return search(id,Root.left)
def deleteNode(root, id):
    if root is None:
        return root

    if id < root.id:
        root.left = deleteNode(root.left, id)

    elif id > root.id:
        root.right = deleteNode(root.right, id)

    else:
        # حالة 0 أو 1 ابن
        if root.left is None:
            return root.right
        elif root.right is None:
            return root.left

        # حالة ابنين
        temp = findMin(root.right)
        root.id = temp.id
        root.name = temp.name
        root.price = temp.price
        root.category = temp.category
        root.product = temp.product

        root.right = deleteNode(root.right, temp.id)

    return root


def displayPro(root, Name):

    # Base case
    if root is None:
        return


    displayPro(root.left, Name)


    current = root.product
    while current is not None:
        if current.name == Name:
            root.display()  # أو root.display() إن وجدت
            break
        current = current.next


    displayPro(root.right, Name)
def replace(root,Name,new):
    # Base case
    if root is None:
        return

    replace(root.left, Name,new)

    current = root.product
    while current is not None:
        if current.name == Name:
            current.name= new
            root.display()
            print("Done !")
            break
        current = current.next

    replace(root.right, Name ,new)
def Modify(id,root):
    if root.id == id :
        ch= int(input("what do u want to modify ? \n 1-name \n 2-price \n 3-category  \n  give ur answer :"))
        match ch :
            case 1:
                 NAME = input("insert your drug  New Name : ")
                 root.name = NAME
            case 2 :
                 PRICE = float(input("insert your drug New price: "))
                 root.price = PRICE
            case 3 :
                CATG = input("insert your drug New category : ")
                root.category = CATG

        return True
    elif root.right == None and root.right == None:
        if root.id == id:
            Modify(id,root)
        else:
            print("the drug is unexecuted !! ")
            return False

    else:
        if id > root.id:
            return Modify(id, root.right)
        else:
            return Modify(id, root.left)


#------------------------ GUI helpers (new: they reuse Node / insert, nothing above was changed) -----------
def addDrug(root, id, name, price, category, product_text):
    New = Node(int(id), name, float(price), category, product_text)
    return insert(root, New)

def modifyDrug(root, id, field, value):
    # same BST walk as search/Modify, but without input()
    while root is not None and root.id != id:
        if id > root.id:
            root = root.right
        else:
            root = root.left
    if root is None:
        print("the drug is unexecuted !! ")
        return False
    if field == "name":
        root.name = value
    elif field == "price":
        root.price = float(value)
    elif field == "category":
        root.category = value
    root.display()
    print("Done !")
    return True


if __name__ == "__main__":
    #program Start -----------------------------------------------------------------------------------

    end=True
    root=BuildTree("drug.txt")


    while end:
        print("------------------------Welcome to the Drug Administration !!----------------------------------------------")
        print(
            " \n 1-Inserting Drug \n 2- View the list of drugs \n 3-Searching for a drug by ID \n 4-Delete a specific drug by ID \n 5-Delete a product of drug \n 6-display all drugs containing the same product \n 7-Replacing one product in all product lists \n 8- Modify by id \n 9- exit ")

        pick = int(input(" insert your choice "))
        match pick:
            case 1:
                NewRoot = addNode(root)
                print("the drug added successfully !!")
            case 2:
                inOrder(root)

            case 3:
                try:
                    id = int(input("insert the id to search : "))
                except ValueError:
                    print("Id must by integer ")

                search(id, root)

            case 4:
                try:
                    id = int(input("insert the id to delete : "))
                except ValueError:
                    print("Id must by integer ")

                root = deleteNode(root, id)
                print("the drug deleted successfully !")

            case 5:
                try:
                    id = int(input("insert the id to delete its product : "))
                except ValueError:
                    print("Id must by integer ")

                name = input(" give name of product : ")
                deletProduct(root, id, name)

            case 6:
                proName = input("give product name : ")
                displayPro(root, proName)

            case 7:
                proName = input("give product name : ")
                newName = input("give product new name : ")
                replace(root, proName, newName)
            case 8:
                try:
                    id = int(input("Give Id to Modify"))
                except ValueError:
                    print("Id must by integer ")

                Modify(id,root)

            case 9:
                saveTree(root, "drug.txt")
                end = False
            case _:
                print("the value is wrong ! chose from the list ")
