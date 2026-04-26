# LeetCode
# 122. Best Time to Buy and Sell Stock II
# Medium
# You are given an integer array prices where prices[i] is the price of a given stock on the ith day.
#
# On each day, you may decide to buy and/or sell the stock. You can only hold at most one share of the stock at any
# time. However, you can sell and buy the stock multiple times on the same day, ensuring you never hold more than one
# share of the stock.
#
# Find and return the maximum profit you can achieve.
from typing import List


class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        income = 0
        for day in range(len(prices) - 1):
            if prices[day] < prices[day + 1]:
                income += prices[day + 1] - prices[day]
        return income


prices = [7, 1, 5, 3, 6, 4]
prices = [1, 2, 3, 4, 5]
prices = [7, 6, 4, 3, 1]
print(Solution().maxProfit(prices))

# Здесь не очевидный момент в том, что мы не должны искать оптимально возможную дату для продажи.
# 1. Всё сводится к продаже сразу, как только видим рост цен.
# 2. + прибыль плавно размазана на всём сроке. Она не кроется в разнице между конкретными датами. Разница между
# датами, по сути это подмножество всех размазанных разниц.
# 3. Мы можем продать => т.е фикисровать прибыль и сразу же покупать назад эту же акцию. На общем горизонте цены
# сократятся -p0 + p1 - p1 + p2

