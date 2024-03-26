class TemporalInformationContentCalculator:
    def __init__(self):
        self.TemporalRelations = {}
        self.EventProbabilities = {}
    
    def calculate_temporal_information_content(self, traces, lambda_val):
        IC_Temporal = {}
        # Assuming extract_temporal_relations and estimate_event_probabilities are revised to handle dictionaries
        self.extract_temporal_relations(traces)
        self.estimate_event_probabilities(traces)
        for trace in traces:
            for event in trace:
                # Assuming 'concept:name' as the unique identifier for each event
                event_id = event['concept:name']
                P_a = self.get_event_probability(event_id)
                TemporalContext = self.get_temporal_context(event_id)
                AdjustedProbability = self.adjust_probability_for_temporal_context(P_a, TemporalContext)
                if AdjustedProbability > 0:
                    IC_Temporal[event_id] = -lambda_val * math.log2(AdjustedProbability)
                else:
                    IC_Temporal[event_id] = float('inf')
        return IC_Temporal


    def extract_temporal_relations(self, event):
        TemporalContext = {}
        for event_pair, time_interval in self.TemporalRelations.items():
            if event in event_pair:
                TemporalContext[event_pair] = time_interval
        return TemporalContext
    
    def estimate_event_probabilities(self, traces):
        event_frequencies = {}
        total_events = sum(len(trace) for trace in traces)

        for trace in traces:
            for event in trace:
                # Directly access 'concept:name' for the event identifier
                event_id = event['concept:name']

                if event_id in event_frequencies:
                    event_frequencies[event_id] += 1
                else:
                    event_frequencies[event_id] = 1

        # Calculate event probabilities
        for event_id, frequency in event_frequencies.items():
            self.EventProbabilities[event_id] = frequency / total_events



    def get_event_probability(self, event):
        if event in self.EventProbabilities:
            return self.EventProbabilities[event]
        else:
            return 0

    def get_temporal_context(self, event):
        TemporalContext = {}
        for event_pair, time_interval in self.TemporalRelations.items():
            if event in event_pair:
                TemporalContext[event_pair] = time_interval
        return TemporalContext

    def adjust_probability_for_temporal_context(self, P_a, TemporalContext):
        AdjustedProbability = P_a
        for event_pair, time_interval in TemporalContext.items():
            AdjustmentFactor = self.calculate_adjustment_factor(time_interval)
            AdjustedProbability *= AdjustmentFactor
        return AdjustedProbability

    def calculate_time_interval(self, event1, event2):
        # Example implementation: calculate the time interval in seconds
        return (event2 - event1).total_seconds()

    def calculate_event_frequencies(self, event_log):
        # Example implementation: calculate the frequencies of events in the event log
        event_frequencies = {}
        for event in event_log:
            if event in event_frequencies:
                event_frequencies[event] += 1
            else:
                event_frequencies[event] = 1
        return event_frequencies

    def calculate_adjustment_factor(self, time_interval):
        # Example implementation: calculate the adjustment factor based on the time interval
        return math.exp(-time_interval / 60)  # Adjusted factor using an exponential decay function
