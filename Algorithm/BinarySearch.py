# def binarySearch(arr, item):
#     low = 0
#     high = len(arr) - 1
#     n = 0
#     while low <= high:
#         n += 1
#         mid = (low + high) // 2
#         guess = arr[mid]
#
#         if guess == item:
#             return (mid, n)
#
#         if guess > item:
#             high = mid - 1
#
#         else:
#             low = mid + 1
#
#     return None
#
#
# arr = [i for i in range(100)]
# print(arr)
# item = 20
# print(binarySearch(arr, item))




def binarySearch_Dict(dict1, x, y ,z):
    low = 0
    high = len(dict1) - 1
    n = 0

    # control test domain
    while low <= high:
        n += 1
        mid = (low + high) // 2
        guessItem = dict1[mid]
        guessx, guessy, guessz =

        if guess == item:
            return (mid, n)

        if guess > item:
            high = mid - 1

        else:
            low = mid + 1

    return None


arr = [i for i in range(100)]
print(arr)
item = 20
print(binarySearch(arr, item))











