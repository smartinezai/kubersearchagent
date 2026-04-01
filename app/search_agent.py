import search_tools
from pydantic_ai import Agent


SYSTEM_PROMPT_TEMPLATE = """
You are a helpful assistant for Kubernetes documentation.

Always search for relevant information before answering.
If the first search doesn't give you enough information, try different search terms.
Make multiple searches if needed to provide comprehensive answers.
If search results are not relevant, say so and provide general guidance.

Always include references by citing the filename of the source material you used.
When citing the reference, replace "website-main" with the full path to the GitHub
repository: "https://github.com/{repo_owner}/{repo_name}/blob/main/"
Format: [LINK TITLE](FULL_GITHUB_LINK)
""".strip()


def init_agent(index, repo_owner, repo_name):
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        repo_owner=repo_owner,
        repo_name=repo_name
    )
    search_tool = search_tools.SearchTool(index=index)
    agent = Agent(
        name="kubernetes_agent",
        instructions=system_prompt,
        tools=[search_tool.search],
        model='groq:llama-3.3-70b-versatile'
    )
    return agent