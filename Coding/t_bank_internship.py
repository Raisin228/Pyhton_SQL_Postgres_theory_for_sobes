def solve():
    n, x = map(int, input().split())
    a = list(map(int, input().split()))

    d = [0] * n
    rem = x
    for i in range(n - 1, -1, -1):
        d[i] = rem // a[i]
        rem %= a[i]

    INF = float('inf')

    dp = [0, INF]

    for i in range(n):
        new_dp = [INF, INF]
        ratio = a[i + 1] // a[i] if i + 1 < n else None

        for carry in range(2):
            if dp[carry] == INF:
                continue

            need = d[i] + carry

            new_dp[0] = min(new_dp[0], dp[carry] + need)

            if ratio is not None and need < ratio:
                change = ratio - need
                new_dp[1] = min(new_dp[1], dp[carry] + change)

        dp = new_dp

    print(dp[0])


solve()
