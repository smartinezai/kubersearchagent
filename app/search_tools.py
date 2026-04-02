from typing import List, Any


class SearchTool:
    def __init__(self, index):
        self.index = index

    def search(self, query: str) -> List[Any]:
        """
        Search the Kubernetes documentation using text search.

        Args:
            query (str): The search query string.

        Returns:
            List[Any]: A list of up to 2 relevant chunks from the Kubernetes docs.
        """
        return self.index.search(query, num_results=2)