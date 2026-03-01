from .data_interface import TimeSeriesProvider
from .engine import EcosystemGraphEngine
from .governance import ExpansionController
from .llm_interface import GroqLLM
from .validation import StatisticalValidator


def run(symbol, data_provider=None, llm=None, validator=None, controller=None):
    engine = EcosystemGraphEngine(
        llm=llm or GroqLLM(),
        data_provider=data_provider or TimeSeriesProvider(),
        validator=validator or StatisticalValidator(),
        controller=controller or ExpansionController(),
    )

    bundle = engine.build(symbol)
    return bundle.nodes, bundle.edges
