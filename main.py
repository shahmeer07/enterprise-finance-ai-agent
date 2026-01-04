from agent.orchestrator import run_agent

def main():
    print("Enterprise Finance Agent is running. ")
    print("Type 'exit'  to Quit .\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit" , 'quit']:
            print("Agent: Cheers mate, until next time!")
            break

        response = run_agent(user_input)
        print("\nAgent: " , response , "\n")

if __name__ == "__main__":
    main()
