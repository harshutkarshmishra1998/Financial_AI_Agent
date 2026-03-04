from pathlib import Path
import matplotlib.pyplot as plt
from market_signal.engine import run
from market_signal.advanced_plots import (
    plot_full_signal_context,
    anomaly_heatmap,
    regime_visualizer,
    signal_vs_volatility
)


def run_signal_pipeline(symbol: str, start: str, end: str, run_id: str):
    
    # Run signal engine
    events = run(
        symbol=symbol,
        start=start,
        end=end,
        run_id=run_id
    )
    
    run_dir = Path("data") / run_id
    plots_dir = run_dir / "plots"

    plots_dir.mkdir(parents=True, exist_ok=True)

    # Generate analytics plots
    plot_full_signal_context(run_id, symbol)
    plt.savefig(plots_dir / "full_context.png")

    anomaly_heatmap(run_id)
    plt.savefig(plots_dir / "anomaly_heatmap.png")

    regime_visualizer(run_id)
    plt.savefig(plots_dir / "regime_visualizer.png")
    
    signal_vs_volatility(run_id)
    plt.savefig(plots_dir / "signal_vs_volatility.png")

    return events