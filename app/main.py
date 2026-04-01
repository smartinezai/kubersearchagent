import asyncio
import ingest
import search_agent
import logs

REPO_OWNER = "kubernetes"
REPO_NAME = "website"


def initialize_index():
    print(f"Starting Kubernetes AI Assistant for {REPO_OWNER}/{REPO_NAME}")
    print("Initializing data ingestion...")
    index = ingest.index_data(REPO_OWNER, REPO_NAME)
    print("Data indexing completed successfully!")
    return index


def initialize_agent(index):
    print("Initializing search agent...")
    agent = search_agent.init_agent(index, REPO_OWNER, REPO_NAME)
    print("Agent initialized successfully!")
    return agent


def main():
    index = initialize_index()
    agent = initialize_agent(index)

    while True:
        question = input("Your question: ")
        if question.strip().lower() == 'stop':
            print("Goodbye!")
            break

        print("Thinking...")
        response = asyncio.run(agent.run(user_prompt=question))
        logs.log_interaction_to_file(agent, response.new_messages())
        print(f"\nAnswer:\n{response.output}")
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()