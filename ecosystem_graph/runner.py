from .engine import EcosystemGraphEngine, GraphNode
from .llm_interface import GroqLLM
from .data_interface import TimeSeriesProvider
from .validation import StatisticalValidator
from .governance import ExpansionController


def run(symbol):

    seed = GraphNode(
        id=symbol,
        name=symbol,
        node_type="company",
        economic_layer="core"
    )

    engine = EcosystemGraphEngine(
        llm=GroqLLM(),
        data_provider=TimeSeriesProvider(), 
        validator=StatisticalValidator(),
        controller=ExpansionController()
    )

    engine.add_node(seed)
    engine.expand(seed)

    return engine.nodes, engine.edges