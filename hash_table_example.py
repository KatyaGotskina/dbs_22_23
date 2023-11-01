from hashlib import md5


class Node:
    def __init__(self, value, key, next=None) -> None:
        self.value = value
        self.key = key
        self.next = next

class HashT:
    def __init__(self, capacity=10) -> None:
        self.capacity = capacity
        self.buckets = [None] * self.capacity
    
    @staticmethod
    def get_hash(value: str):
        return int(md5(value.encode('utf-8')).hexdigest(), 16) % 10

    def insert(self, key, value):
        ind = self.get_hash(key)
        if not self.buckets[ind]:
            self.buckets[ind] = Node(key, value)
        else:
            bucket = self.buckets[ind]
            while bucket.next:
                bucket = bucket.next
            bucket.next = Node(key, value)
    
    def search(self, key):
        res = []
        ind = self.get_hash(key)
        node = self.buckets[ind]
        while node:
            if node.key == key:
                res.append(node.value)
            node = node.next
        return res


hash_table = HashT()
hash_table.insert('pc', {'name' : 'mac pro', 'price' : 5000})
hash_table.insert('smartphones', {'name' : 'iPhone', 'price' : 2000})
hash_table.insert('laptop', {'name' : 'honor', 'price' : 3000})
print(hash_table.buckets)