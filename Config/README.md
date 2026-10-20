# Config

Project-level settings for the simulated exchange. The engine does not read these files yet.

This directory is separate from [Market/configs](../Market/configs). Those files are the scenario skeleton. They are not a runnable market, and they do not restate these defaults.

The values here record rules from the [exchange rulebook](../Research/exchange-rulebook.md). They do not add behavior. Comments name the rule.

| File | What it records |
| --- | --- |
| [instrument.yaml](instrument.yaml) | Stock `JPM`, tick size, and LULD defaults |
| [accounts.yaml](accounts.yaml) | Cash account, buying power, and no short sales |
| [matching.yaml](matching.yaml) | Continuous session, self-trade prevention, modification, and validation rejections |
| [limits.yaml](limits.yaml) | Minimum and maximum quantity, left unset |
