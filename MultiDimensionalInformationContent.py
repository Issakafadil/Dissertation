class MultiDimICCalculator:
    def __init__(self, event_log):
        self.event_log = event_log
        self.IC_MultiDim = {}
        # Additional structures for optimized computation
        self.activity_frequency = defaultdict(int)
        self.combination_frequency = defaultdict(int)

    def calculate(self):
        self.calculate_frequencies()
        self.calculate_information_content()
        return self.IC_MultiDim

    def calculate_frequencies(self):
        print("Calculating frequencies...")
        activity_counter = Counter()
        combination_counter = Counter()

        for trace in self.event_log:
            activities = [event['concept:name'] for event in trace]
            activity_counter.update(activities)
            # For simplicity, considering pairs (or customize for more combinations)
            combinations_in_trace = chain.from_iterable(combinations(set(activities), r) for r in range(2, 3))
            combination_counter.update(combinations_in_trace)

        self.activity_frequency = dict(activity_counter)
        self.combination_frequency = dict(combination_counter)
        print("Frequencies calculation complete.")

    def calculate_information_content(self):
        total_events = sum(self.activity_frequency.values())
        print("Calculating Information Content...")
        # Calculate IC for individual activities
        for activity, freq in self.activity_frequency.items():
            probability = freq / total_events
            self.IC_MultiDim[frozenset([activity])] = -math.log2(probability)

        # Calculate IC for combinations
        for combination, freq in self.combination_frequency.items():
            probability = freq / total_events
            self.IC_MultiDim[frozenset(combination)] = -math.log2(probability)

        print("Information Content calculation complete.")
