# Simple usage
from similarweb_api_class import SimilarwebDigitalRankAPI

api_key = "abb5c6f698e6474cbddca689a2ce613f"
client = SimilarwebDigitalRankAPI(api_key)

# Get top 10 websites
top_sites = client.get_top_sites(10)
print(top_sites)

# # Get rank for a specific domain
# rank_data = client.get_website_rank("google.com")
# print(rank_data)

# Check your remaining API credits
status = client.get_subscription_status()
print(status)