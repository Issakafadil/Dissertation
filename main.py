xes_dir_path = './Data'  # to the location of your .xes files (event logs)
parser = XESParser(xes_dir_path)
event_log = parser.process_all_xes_files(max_traces = 100) # you can set the max traces to whatever number. for computational purposes we used 100
print(f"Total traces processed: {len(event_log)}")
lambda_val = 0.5

# Temporal Information Content
calculator = TemporalInformationContentCalculator()
IC_Temporal = calculator.calculate_temporal_information_content(event_log, lambda_val)

# Contextual Information Content
calculator = ContextualInformationContentCalculator(event_log, lambda_val)
IC_Contextual = calculator.calculate_contextual_information_content()

# multi-dimensional Information Content
calculator = MultiDimICCalculator(event_log)
IC_MultiDim = calculator.calculate()


# call the iic function
parsed_log = improved_information_content_algorithm(event_log, IC_Temporal, IC_Contextual, IC_MultiDim, IC_Uncertainty)



# Process Discovery Algorithm
# Predefined thresholds for relationships
sequence_threshold = 0.2
parallel_threshold_max = 1.0
choice_threshold = 1.0

inferred_relationships = []
for i in range(len(parsed_log ) - 1):
    activity, ic = parsed_log [i]
    next_activity, next_ic = parsed_log [i + 1]
    ic_diff = abs(next_ic - ic)
    
    if ic_diff <= sequence_threshold:
        inferred_relationships.append((activity, next_activity, 'sequence'))
    elif sequence_threshold < ic_diff <= parallel_threshold_max:
        inferred_relationships.append((activity, next_activity, 'parallel'))
    elif ic_diff > choice_threshold:
        inferred_relationships.append((activity, next_activity, 'choice'))
print(inferred_relationships)


# Initialize Petri net and markings
net = PetriNet("Constructed Net")
initial_marking = Marking()
final_marking = Marking()

# Helper functions for Petri net construction
def add_place(net, name=None):
    place = petri_utils.add_place(net, name if name else str(uuid.uuid4()))
    return place

def add_transition(net, activity_name):
    transition = petri_utils.add_transition(net, label= activity_name)
    return transition

def add_arc_from_to(source, target, net):
    petri_utils.add_arc_from_to(source, target, net)

# Start construction with initial place
start_place = add_place(net, "start")
initial_marking[start_place] = 1

# Dictionary to keep track of the last place for each activity
last_places = {}



# Function to handle adding sequence structures
def handle_sequence(source_activity, target_activity):
    source_transition = add_transition(net, source_activity)
    if source_activity in last_places:
        source_place = last_places[source_activity]
    else:
        source_place = start_place
    add_arc_from_to(source_place, source_transition, net)
    
    target_place = add_place(net)
    add_arc_from_to(source_transition, target_place, net)
    
    target_transition = add_transition(net, target_activity)
    add_arc_from_to(target_place, target_transition, net)
    
    next_place = add_place(net)
    add_arc_from_to(target_transition, next_place, net)
    last_places[target_activity] = next_place

# Function to handle adding parallel structures
def handle_parallel(source_activity, parallel_activities):
    # Assuming parallel_activities is a list of activities parallel to source_activity
    divergence_place = last_places.get(source_activity, start_place)
    for activity in parallel_activities:
        parallel_transition = add_transition(net, activity)
        add_arc_from_to(divergence_place, parallel_transition, net)
        
        parallel_place = add_place(net)
        add_arc_from_to(parallel_transition, parallel_place, net)
        last_places[activity] = parallel_place

# Function to handle adding choice structures
def handle_choice(source_activity, choice_activities):
    choice_place = last_places.get(source_activity, start_place)
    for activity in choice_activities:
        choice_transition = add_transition(net, activity)
        add_arc_from_to(choice_place, choice_transition, net)
        
        next_place = add_place(net)
        add_arc_from_to(choice_transition, next_place, net)
        last_places[activity] = next_place


# Process inferred relationships to construct the Petri net
for i, (activity, next_activity, rel_type) in enumerate(inferred_relationships):
    if rel_type == 'sequence':
        handle_sequence(activity, next_activity)
    elif rel_type == 'parallel':
        # Collect all activities that are parallel to the current one
        parallel_activities = [next_activity] + [act for act, nxt, typ in inferred_relationships[i+1:] if typ == 'parallel' and act == activity]
        handle_parallel(activity, parallel_activities)
    elif rel_type == 'choice':
        # Collect all possible choice paths from the current activity
        choice_activities = [next_activity] + [act for act, nxt, typ in inferred_relationships[i+1:] if typ == 'choice' and act == activity]
        handle_choice(activity, choice_activities)

# Identify end activities correctly
end_activities = set([activity for activity, _, _ in inferred_relationships])
for _, next_activity, _ in inferred_relationships:
    end_activities.discard(next_activity)  # Remove any activity that is a "next" activity

# Connect end activities to the final transition
final_transition = add_transition(net, "End")
for activity, place in last_places.items():
    if activity not in [act for act, _, _ in inferred_relationships[:-1]]:
        add_arc_from_to(place, final_transition, net)
        
        
# Connect identified end activities' last places to the final transition
for activity in end_activities:
    if activity in last_places:
        add_arc_from_to(last_places[activity], final_transition, net)


# Ensure the 'end' place is correctly defined and added to the Petri net
end_place = add_place(net, "end")
add_arc_from_to(final_transition, end_place, net)
       
# end_place = add_place(net, "end")
# add_arc_from_to(final_transition, end_place, net)
final_marking[end_place] = 1

# Visualization
parameters = {'format': 'pdf', 'debug': False, 'show_labels': True}
# gviz = viz_apply(net, initial_marking, final_marking, parameters=parameters)
# viz_view(gviz)


gviz = pn_visualizer.apply(net, initial_marking, final_marking, parameters=parameters)
pn_visualizer.save(gviz, "images/petri_net1.pdf")
pn_visualizer.view(gviz)
