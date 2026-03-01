from .data_interface import LLMDrivenEconomicProvider, TimeSeriesProvider
from .engine import EcosystemGraphEngine
from .governance import ExpansionController
from .llm_interface import GroqLLM
from .validation import StatisticalValidator


def run(symbol, start=None, end=None, data_provider=None, llm=None, validator=None, controller=None):
    llm = llm or GroqLLM()
    engine = EcosystemGraphEngine(
        llm=llm,
        data_provider=data_provider or LLMDrivenEconomicProvider(llm=llm, start=start, end=end),
        validator=validator or StatisticalValidator(),
        controller=controller or ExpansionController(),
    )

    bundle = engine.build(symbol)
    return bundle.nodes, bundle.edges
