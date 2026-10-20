# Market

Proposed layout for the Project 1 exchange. This is a starting tree, not a rigid rule and not a working system.

Code waits on rulebook review. Read [the exchange rulebook](../Research/exchange-rulebook.md) first. Matching, accounts, validation, and LULD are not implemented, including the rules that are already decided. Every Python module names a future responsibility and stops. Project defaults live in [Config](../Config/README.md). The engine does not read them yet.

Nothing here runs a simulation.

## Layout

| Path | Future responsibility |
| --- | --- |
| `pyproject.toml` | Package metadata only. Python >= 3.11. It does not claim a simulation runs. |
| `configs/baseline.yaml` | Commented keys for a later baseline-liquidity scenario. Not runnable. |
| `configs/low_liquidity.yaml` | Commented keys for a later sparse-trading scenario. Not runnable. |
| `src/market/models.py` | Orders, trades, events |
| `src/market/order_book.py` | Bids, asks, price levels |
| `src/market/matching_engine.py` | Matching rules |
| `src/market/gateway.py` | Order validation |
| `src/market/accounts.py` | Positions and cash |
| `src/market/market_data.py` | Quotes, depth, trade feed |
| `src/market/scheduler.py` | Simulated event queue |
| `src/market/participants.py` | Simple scripted traders |
| `src/market/metrics.py` | Market statistics |
| `src/market/runner.py` | Starts and controls a simulation |
| `tests/test_order_book.py` | Book invariants, once a book exists |
| `tests/test_matching.py` | Price-time and fill invariants |
| `tests/test_accounts.py` | Cash and position invariants |
| `tests/test_market_data.py` | Rebuild-the-book invariant |
| `tests/test_replay.py` | Replay reproduces the same final state |
| `experiments/run_scenario.py` | Run a named scenario after the engine exists |
| `notebooks/market_analysis.ipynb` | Analysis stub. Analysis comes after the engine exists |

Behavior, when it is written, belongs in the milestones in [Research/milestones.md](../Research/milestones.md). The order book comes before matching. Fees and position limits come after accounting is correct.
