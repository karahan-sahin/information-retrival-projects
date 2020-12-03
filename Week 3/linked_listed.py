# Whole structure is in loop 
# instances --> linked list
# linked


class posting:
    def __init__(self, data = None):
        self.data = data
        self.instances = instance_list()
        self.next = None

class instance:
    def __init__(self, data = None):
        self.data = data
        self.next = None

class instance_list:
    def __init__(self):
        self.head = instance()

    def append(self, data):
        new_node = instance(data)
        current = self.head

        while current.next != None:
            current = current.next
        
        current.next = new_node

    def length(self):
        current = self.head
        total = 0
        while current.next != None:
            total +=1
            current = current.next
        return total

    def get(self,index):
        
        if index >= self.length():
            # Fix error
            print("EnvironmentError") 
            return None

        current_node = self.head
        current_index = 0
        while current_index < index:
            current_node = current_node.next
            current_index+=1
        return current_node.data

    def instanceIntersection(self, instance_l1, instance_l2):

        merge_list = self.head

        l1_head = instance_l1.head
        l2_head = instance_l2.head

        while l1_head.next != None or l2_head.next != None:
            print("----------")
            print(l1_head.data)
            print(l2_head.data)
            if l1_head.data == l2_head.data:
                merge_list = posting(l1_head.data)
                merge_list = merge_list.next
                l1_head = l1_head.next
                l2_head = l2_head.next
            elif l1_head.data < l2_head.data:
                l1_head = l1_head.next
            else:
                l2_head = l2_head.next

        return 


class posting_list:
    def __init__(self):
        self.head = posting()

    def append(self, data):
        new_node = posting(data)
        current = self.head

        if current.data == None:
            current = new_node
            return True

        while current.next != None:
            current = current.next
        
        current.next = new_node

    def length(self):
        current = self.head
        total = 0
        while current.next != None:
            total +=1
            current = current.next
        return total

    def display(self):
        elems = []
        current_node = self.head
        while current_node.next != None:
            current_node = current_node.next
            elems.append(current_node.data)
        print(elems)

    def get(self,index):
        
        if index >= self.length():
            # Fix error
            print("EnvironmentError") 
            return None

        current_node = self.head
        current_index = 0
        while current_index < index:
            current_node = current_node.next
            current_index+=1
        return current_node.data

    def delete(self,index):
        if index >= self.length():
            print(EOFError)
            return None

        current_node = self.head
        current_index = 0
        while True:
            last_node = current_node
            current_node = current_node.next
            if current_index == index:
                last_node.next = current_node.next
                return
            current_index+=1  

    def appendInstance(self, posting, position):
        current_node = self.head

        while current_node.data != posting:
            current_node = current_node.next
        
        current_node.instances.append(position)

    def displayInstance(self, posting):
        current_node = self.head

        while current_node.data != posting:
            current_node = current_node.next

        current = current_node.instances.head
        elems = []
        while current.next != None:
            current = current.next
            elems.append(current.data)
        print(elems)

    def getIntersection(self, linked_list1, linked_list2):
        
        merge_list = self.head

        l1_head = linked_list1.head
        l2_head = linked_list2.head

        while l1_head.next != None or l2_head.next != None:
            print("----------")
            print(l1_head.data)
            print(l2_head.data)
            if l1_head.data == l2_head.data:
                merge_list = posting(l1_head.data)
                merge_list = merge_list.next
                l1_head = l1_head.next
                l2_head = l2_head.next
            elif l1_head.data < l2_head.data:
                l1_head = l1_head.next
            else:
                l2_head = l2_head.next

        return 
                



llist1 = posting_list()

llist2 = posting_list()

llist1.append(1)
llist1.appendInstance(1,1)
llist1.appendInstance(1,2)
llist1.appendInstance(1,3)
llist1.append(2)
llist1.append(4)
llist1.append(11)
llist1.append(31)
llist1.append(173)
llist1.append(174)
llist1.append(175)



llist2.append(2)
llist2.append(31)
llist2.append(54)
llist2.append(101)
llist2.append(175)

# to, 993427:
# h 1, 6: h7, 18, 33, 72, 86, 231i;
# 2, 5: h1, 17, 74, 222, 255i;
# 4, 5: h8, 16, 190, 429, 433i;
# 5, 2: h363, 367i;
# 7, 3: h13, 23, 191i; . . . i
# be, 178239:
# h 1, 2: h17, 25i;
# 4, 5: h17, 191, 291, 430, 434i;
# 5, 3: h14, 19, 101i; . . . i

llist1.displayInstance(1)    

merge_list = posting_list()
merge_list.getIntersection(llist1, llist2)

merge_list.display()