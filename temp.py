# ==============================================================================
# File: temp.py
# Project: allison
# File Created: Tuesday, 28th December 2021 9:58:28 am
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 28th December 2021 9:58:33 am
# Modified By: Dillon Koch
# -----
#
# -----
# nothing important
# ==============================================================================

# * recursion
# def fib(n):
#     if n <= 2:
#         return 1
#     else:
#         return fib(n-1) + fib(n-2)

# * memoization
# def fib(n):
#     memo = {1: 1, 2: 1}
#     count = 3
#     while count <= n:
#         memo[count] = memo[count - 1] + memo[count - 2]
#         count += 1
#     return memo[n]

# ! grid traveler

# * recursion


# def grid(m, n):
#     if (m == 0) or (n == 0):
#         return 0
#     elif (m == 1) and (n == 1):
#         return 1
#     return grid(m - 1, n) + grid(m, n - 1)


# * memoization

# def grid(m, n, memo={}):
#     if (m == 0) or (n == 0):
#         return 0
#     elif (m == 1) or (n == 1):
#         return 1

#     if (m, n) in memo:
#         return memo[(m, n)]
#     else:
#         memo[(m, n)] = grid(m - 1, n, memo) + grid(m, n - 1, memo)
#         return memo[(m, n)]

# ! linked list traversal

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


a = Node('A')
b = Node('B')
c = Node('C')
d = Node('D')

a = Node(1)
b = Node(2)
c = Node(3)
d = Node(4)

a.next = b
b.next = c
c.next = d


# def listvalues(head):
#     values = []
#     current = head
#     while current:
#         values.append(current.value)
#         current = current.next
#     return values

# def listvalues(head, values=[]):
#     if head is None:
#         return values
#     values.append(head.value)
#     return listvalues(head.next, values)

# def sumlist(head):
#     total = 0
#     current = head
#     while current:
#         total += current.value
#         current = current.next
#     return total

def sumlist(head, total=0):
    if head is None:
        return total
    total += head.value
    return sumlist(head.next, total)

# def printlist(head):
#     current = head
#     if current is None:
#         return None
#     else:
#         print(current.value)
#         printlist(current.next)

# def printlist(head):
#     if head is None:
#         return None
#     print(head.value)
#     printlist(head.next)

# def printlist(head):
#     current = head
#     while current:
#         print(current.value)
#         current = current.next


if __name__ == '__main__':
    # for i in range(10):
    #     for j in range(10):
    #         print(i, j)
    #         print(grid(i, j))

    print(sumlist(a))
