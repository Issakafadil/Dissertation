class UncertaintyICCalculator:
    def __init__(self, event_log):
        self.event_log = event_log
        self.expected_attributes = ['concept:name', 'time:timestamp', 'resource']  # Example expected attributes
        self.IC_Uncertainty = {}
        self.event_probabilities = self.estimate_event_probabilities()
        self.uncertainty_factors = self.quantify_uncertainty_factors()

    def estimate_event_probabilities(self):
        event_counter = Counter(event['concept:name'] for trace in self.event_log for event in trace)
        total_events = sum(event_counter.values())
        return {event: count / total_events for event, count in event_counter.items()}

    def quantify_uncertainty_factors(self):
        uncertainty_factors = {}
        event_names = set(event['concept:name'] for trace in self.event_log for event in trace)
        for index, event_name in enumerate(event_names, start=1):
            missing_data, inconsistency, variability = self.measure_missing_data(event_name)
            total_uncertainty = missing_data + inconsistency + variability
            uncertainty_factors[event_name] = total_uncertainty
            # Progress bar update
            self.print_progress(index, len(event_names), prefix='Quantifying Uncertainty Factors:')
        return uncertainty_factors

    def measure_missing_data(self, event_name):
        missing_data_count = inconsistency_score = variability_score = 0
        attribute_values = defaultdict(set)
        for trace in self.event_log:
            for event in trace:
                if event['concept:name'] == event_name:
                    missing_data_count += sum(1 for attr in self.expected_attributes if attr not in event)
                    for attr, value in event.items():
                        if attr not in self.expected_attributes:
                            inconsistency_score += 1
                        if isinstance(value, str) and not value.isdigit():
                            inconsistency_score += 1
                        attribute_values[attr].add(value)
        for attr, values in attribute_values.items():
            if len(values) > 1:
                variability_score += len(values) - 1
        return missing_data_count, inconsistency_score, variability_score

    def calculate(self):
        total_events = len(self.event_probabilities)
        for index, (event_name, probability) in enumerate(self.event_probabilities.items(), start=1):
            uncertainty = self.uncertainty_factors.get(event_name, 0)
            self.IC_Uncertainty[event_name] = -math.log2(probability + uncertainty)
            # Progress bar update
            self.print_progress(index, total_events, prefix='Calculating IC:')
        return self.IC_Uncertainty

    def print_progress(self, iteration, total, prefix='', length=50, fill='█'):
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% Complete', end='\r')
        if iteration == total:
            print()
