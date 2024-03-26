#IIC - Improved Information Content
def improved_information_content_algorithm(event_log, ic_temporal, ic_contextual, ic_multidim, ic_uncertainty):
    # Invert the uncertainty IC values
    inverted_uncertainty_ic = {activity: -value for activity, value in ic_uncertainty.items()}

    # Function to calculate comprehensive IC for a given activity
    def calculate_comprehensive_ic(activity):
        temp_ic = ic_temporal.get(activity, 0)
        cont_ic = ic_contextual.get(activity, 0)
        multidim_ic = ic_multidim.get(frozenset([activity]), 0)
        unc_ic = inverted_uncertainty_ic.get(activity, 0)
        # Calculate the average IC considering all dimensions
        return (temp_ic + cont_ic + multidim_ic + unc_ic) / 4
    
    # Collect and calculate comprehensive IC for each unique activity in the log
    activity_ic_scores = {}
    for trace in event_log:
        for event in trace:
            activity = event['concept:name']
            if activity not in activity_ic_scores:
                activity_ic_scores[activity] = calculate_comprehensive_ic(activity)
    
    # Sort activities by their comprehensive IC values
    parsed_log= sorted(activity_ic_scores.items(), key=lambda x: x[1], reverse=True)
    
    return parsed_log
