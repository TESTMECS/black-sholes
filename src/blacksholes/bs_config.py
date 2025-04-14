import os
from dotenv import load_dotenv

load_dotenv()


class BlackScholesConfig:
    def __init__(
        self,
        bs_base_url: str = "",
        backoff: bool = True,
        backoff_max_time: int = 30,
    ):
        """
        Initialize the BlackScholesConfig object.
        Parameters
        ----------
        bs_base_url : str
            The base URL for the Black Scholes API.
        backoff : bool
            Whether to use backoff for retries.
        backoff_max_time : int
            The maximum time to wait for a retry.

        """
        self.bs_base_url = bs_base_url or os.getenv("BS_BASE_URL")
        self.backoff = backoff
        self.backoff_max_time = backoff_max_time 
    
    def __str__(self):
        return f"BlackScholesConfig(bs_base_url={self.bs_base_url}, backoff={self.backoff}, backoff_max_time={self.backoff_max_time})"
