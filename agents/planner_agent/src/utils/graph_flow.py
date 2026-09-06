class LongGraphFlow:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.results = {}
    
    def add_node(self, name, agent, input_key, output_key):
        self.nodes.append({
            "name": name,
            "agent": agent,
            "input_key": input_key,
            "output_key": output_key
        })
    
    def add_edge(self, from_node, to_node):
        self.edges.append((from_node, to_node))
    
    def execute(self, initial_input):
        """Execute the graph flow"""
        self.results["input"] = initial_input
        
        for node in self.nodes:
            agent = node["agent"]
            input_data = self.results.get(node["input_key"])
            
            if agent.__class__.__name__ == "PlannerAgent":
                output = agent.parse_prompt(input_data)
            else:
                output = agent.process(input_data)
            
            self.results[node["output_key"]] = output
            print(f"✅ Executed: {node['name']}")
        
        return self.results