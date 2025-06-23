import requests
import json
from typing import Optional, Dict, Any, List

class SimilarwebDigitalRankAPI:
    """
    Python client for Similarweb DigitalRank API
    
    This class provides methods to interact with all three available endpoints:
    1. Top SimilarRank Sites
    2. Website SimilarRank
    3. Get Subscription Status
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the API client with your Similarweb API key
        
        Args:
            api_key (str): Your Similarweb API key
        """
        self.api_key = api_key
        self.base_url = "https://api.similarweb.com"
        self.session = requests.Session()
    
    def get_top_sites(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get the top-ranking websites globally
        
        Args:
            limit (int): Number of results to return (max 100, default 10)
            
        Returns:
            dict: API response containing top sites data
            
        Raises:
            requests.RequestException: If API request fails
        """
        if limit > 100:
            raise ValueError("Limit cannot exceed 100")
            
        url = f"{self.base_url}/v1/similar-rank/top-sites"
        params = {
            'api_key': self.api_key,
            'limit': limit
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Print data points consumed
            data_points_used = response.headers.get('sw-datapoint-charged', 'Unknown')
            print(f"Data points consumed: {data_points_used}")
            
            return response.json()
            
        except requests.RequestException as e:
            print(f"Error fetching top sites: {e}")
            raise
    
    def get_website_rank(self, domain: str) -> Dict[str, Any]:
        """
        Get the global rank of a specific website
        
        Args:
            domain (str): Domain name (e.g., 'google.com')
            
        Returns:
            dict: API response containing website rank data
            
        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.base_url}/v1/similar-rank/{domain}/rank"
        params = {
            'api_key': self.api_key
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Print data points consumed
            data_points_used = response.headers.get('sw-datapoint-charged', 'Unknown')
            print(f"Data points consumed: {data_points_used}")
            
            return response.json()
            
        except requests.RequestException as e:
            print(f"Error fetching website rank for {domain}: {e}")
            raise
    
    def get_subscription_status(self) -> Dict[str, Any]:
        """
        Get remaining monthly data credits in your account
        
        Returns:
            dict: API response containing subscription status
            
        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.base_url}/user-capabilities"
        params = {
            'api_key': self.api_key
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            print(f"Error fetching subscription status: {e}")
            raise
    
    def print_top_sites(self, limit: int = 10) -> None:
        """
        Print top sites in a formatted way
        
        Args:
            limit (int): Number of sites to display
        """
        try:
            data = self.get_top_sites(limit)
            
            print(f"\n🏆 Top {limit} Websites Globally:")
            print("-" * 50)
            
            for i, site in enumerate(data.get('top_sites', []), 1):
                print(f"{i:2d}. {site['site']:<25} (Rank: {site['rank']:,})")
                
        except Exception as e:
            print(f"Error displaying top sites: {e}")
    
    def print_website_rank(self, domain: str) -> None:
        """
        Print website rank in a formatted way
        
        Args:
            domain (str): Domain to check
        """
        try:
            data = self.get_website_rank(domain)
            
            print(f"\n📊 Website Ranking for {domain}:")
            print("-" * 40)
            print(f"Global Rank: {data.get('similar_rank', {}).get('rank', 'N/A'):,}")
            
        except Exception as e:
            print(f"Error displaying website rank: {e}")
    
    def print_subscription_status(self) -> None:
        """
        Print subscription status in a formatted way
        """
        try:
            data = self.get_subscription_status()
            
            print(f"\n💳 Subscription Status:")
            print("-" * 30)
            
            # Extract relevant information from the response
            remaining_hits = data.get('remaining_hits', 'N/A')
            monthly_limit = data.get('monthly_limit', 'N/A')
            
            print(f"Remaining API calls: {remaining_hits}")
            print(f"Monthly limit: {monthly_limit}")
            
            if isinstance(remaining_hits, int) and isinstance(monthly_limit, int):
                used = monthly_limit - remaining_hits
                percentage_used = (used / monthly_limit) * 100
                print(f"Used: {used} ({percentage_used:.1f}%)")
                
        except Exception as e:
            print(f"Error displaying subscription status: {e}")


# Example usage and demo functions
def main():
    """
    Example usage of the Similarweb DigitalRank API client
    """
    
    # Replace with your actual API key
    API_KEY = "abb5c6f698e6474cbddca689a2ce613f"
    
    # Initialize the client
    client = SimilarwebDigitalRankAPI(API_KEY)
    
    try:
        # 1. Check subscription status first
        print("=" * 60)
        print("SIMILARWEB DIGITALRANK API DEMO")
        print("=" * 60)
        
        client.print_subscription_status()
        
        # 2. Get top 5 websites
        client.print_top_sites(limit=5)
        
        # 3. Check specific website ranks
        websites_to_check = ['edtechagency.net']
        
        for domain in websites_to_check:
            client.print_website_rank(domain)
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        print("\nMake sure to:")
        print("1. Replace 'YOUR_SIMILARWEB_API_KEY_HERE' with your actual API key")
        print("2. Check your internet connection")
        print("3. Verify your API key is valid and has remaining credits")


# Alternative simple functions for quick usage
def get_top_websites(api_key: str, limit: int = 10) -> List[Dict]:
    """
    Simple function to get top websites
    
    Args:
        api_key (str): Your Similarweb API key
        limit (int): Number of results
        
    Returns:
        list: List of top websites
    """
    client = SimilarwebDigitalRankAPI(api_key)
    data = client.get_top_sites(limit)
    return data.get('top_sites', [])


def get_domain_rank(api_key: str, domain: str) -> int:
    """
    Simple function to get a domain's rank
    
    Args:
        api_key (str): Your Similarweb API key
        domain (str): Domain to check
        
    Returns:
        int: Global rank of the domain
    """
    client = SimilarwebDigitalRankAPI(api_key)
    data = client.get_website_rank(domain)
    return data.get('similar_rank', {}).get('rank', 0)


if __name__ == "__main__":
    main()