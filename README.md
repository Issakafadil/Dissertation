# Dissertation
PhD Thesis Code on Event Log Processing for Process Mining

This repository contains the Python code developed for my PhD thesis, which focuses on Event Log Processing within the domain of Process Mining. The code is designed to parse event logs in XES format, calculate various forms of information content, and construct process models from the processed data.

The repository is organized into several modules:

XESParser: Handles the parsing of XES files, converting event logs into a structured format for further processing.
TemporalInformationContentCalculator: Calculates the temporal information content of events within a log, considering their temporal relationships.
ContextualInformationContentCalculator: Estimates the contextual information content by considering the surrounding context of each event.
MultiDimICCalculator: Provides functionality to compute multi-dimensional information content based on the relationships between different event attributes.
UncertaintyICCalculator: Measures the uncertainty in information content, which can arise from incomplete or inconsistent data within event logs.
IICCode: Implements an algorithm to calculate improved information content (IIC) across multiple dimensions.
Additionally, the repository includes scripts for the construction of process models from event data, utilizing inferred relationships to build a Petri net representation.

Please refer to the individual scripts for detailed documentation on each component. The code in this repository forms the backbone of the research presented in my thesis and showcases a practical implementation of theoretical concepts in process mining and event log analysis.
