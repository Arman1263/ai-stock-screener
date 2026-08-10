from market_data.angel_auth import AngelAuth


auth = AngelAuth()

auth.login()

print("Angel One login successful")
print("JWT token received:", bool(auth.auth_token))
print("Feed token received:", bool(auth.feed_token))