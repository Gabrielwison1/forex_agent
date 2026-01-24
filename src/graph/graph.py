from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes.strategist import strategist_node
from src.nodes.architect import architect_node

from src.nodes.tactical import tactical_node
from src.nodes.risk_manager import risk_manager_node
from src.execution.oanda_executor import oanda_executor_node

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("tactical", tactical_node)
    workflow.add_node("risk_manager", risk_manager_node)
    workflow.add_node("executor", oanda_executor_node)
    
    # Set Entry Point
    workflow.set_entry_point("strategist")
    
    # Conditional Edge Logic
    def router(state: AgentState):
        bias = state.get("current_bias")
        if bias == "RISK_OFF":
            return "end" # Stop execution
        return "architect" # Continue to 15M analysis
    
    workflow.add_conditional_edges(
        "strategist",
        router,
        {
            "end": END,
            "architect": "architect"
        }
    )
    
    # Flow: Architect -> Tactical -> Risk Manager -> Executor -> END
    workflow.add_edge("architect", "tactical")
    workflow.add_edge("tactical", "risk_manager")
    workflow.add_edge("risk_manager", "executor")
    workflow.add_edge("executor", END)
    
    return workflow.compile()
