import asyncio
from agentic_system.graph import run_graph

async def main():
    """Main entry point to run the agentic system graph."""
    query = "content : 'The integration of Generative AI with Distributed Systems is a pivotal development in modern computing, enabling the creation of highly scalable, reliable, and efficient AI applications. Distributed systems provide the computational backbone necessary to handle the massive datasets and complex computations required for training and deploying large-scale AI models, such as Large Language Models (LLMs). By leveraging distributed computing paradigms, organizations can overcome the limitations of single-machine processing, achieving faster model training times and enabling real-time inference capabilities. This synergy is particularly critical for edge AI applications, where processing needs to occur locally on devices with limited resources. Furthermore, the collaborative nature of distributed systems facilitates the development of federated learning approaches, allowing AI models to be trained on decentralized data sources without compromising user privacy. As the demand for more sophisticated and personalized AI applications continues to grow, the role of distributed systems in supporting and enhancing Generative AI will become increasingly indispensable.'"
    print(f"Running graph with query: {query}")
    
    try:
        result = await run_graph(query)
        print("\n" + "="*50)
        print("FINAL RESPONSE:")
        print("="*50)
        print(result)
        print("="*50)
    except Exception as e:
        print(f"An error occurred during graph execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
