class ContextualInformationContentCalculator:
    def __init__(self, event_log, lambda_val):
        self.event_log = event_log[:5000]  # Limit the event log to the first 5000 traces
        self.lambda_val = lambda_val
        self.context_data = self.extract_contextual_data()

    def extract_contextual_data(self):
        context_data = {}
        total_events = sum(len(trace) for trace in self.event_log)
        processed_events = 0
        print("Extracting contextual data...")
        for trace_index, trace in enumerate(self.event_log, start=1):
            for event in trace:
                event_key = self.create_event_key(event)
                context_data[event_key] = self.extract_attributes(event)
                processed_events += 1
                if processed_events % 100 == 0 or trace_index == len(self.event_log):
                    print(f"Processed {processed_events}/{total_events} events. Trace {trace_index}/{len(self.event_log)}")
        print("Contextual data extraction complete.")
        return context_data

    def create_event_key(self, event):
        # Ensure the event key is created consistently
        return event['concept:name']

    def extract_attributes(self, event):
        # Extract broader attributes for context
        broader_context_keys = ['lifecycle:transition', 'org:group']
        return {key: event.get(key) for key in broader_context_keys}

    def get_contexts(self, event_key):
        # Retrieve context using the consistent event key
        return self.context_data.get(event_key, None)

    def estimate_conditional_probability(self, event, context):
        matching_events = context_occurrences = 0
        for other_event in sum(self.event_log, []): # Flatten the list of traces
            other_event_key = self.create_event_key(other_event)
            if self.is_context_match(other_event, context):
                context_occurrences += 1
                if other_event_key == event:
                    matching_events += 1
        return matching_events / context_occurrences if context_occurrences else 0

    def is_context_match(self, event, context):
        # Check if the event matches the given context
        for key, value in context.items():
            if event.get(key) != value:
                return False
        return True

    
    def calculate_contextual_information_content(self):
        IC_contextual = {}
        total_events = sum(len(trace) for trace in self.event_log)  # Calculate total number of events
        processed_events = 0  # Initialize counter for processed events

        for trace_index, trace in enumerate(self.event_log):
            for event_index, event in enumerate(trace):
                event_key = self.create_event_key(event)
                context = self.get_contexts(event_key)
                if context is not None:
                    p_a_given_c = self.estimate_conditional_probability(event_key, context)
                    IC_value = -self.lambda_val * math.log2(p_a_given_c) if p_a_given_c > 0 else float('inf')
                    IC_contextual[event_key] = IC_value
                else:
                    print(f"No context found for event {event_key}. IC set to Inf.")
                    IC_contextual[event_key] = float('inf')

                processed_events += 1
                # Progress update
                progress_percentage = (processed_events / total_events) * 100
                print(f"\rProgress: {progress_percentage:.2f}%", end='')

        print("\nContextual data calculation complete.")
        return IC_contextual   
