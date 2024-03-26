import xml.etree.ElementTree as ET
from dateutil import parser as date_parser
import os

class XESParser:
    """Parser for XES formatted event logs.

    Attributes:
        xes_dir_path (str): Directory path where XES files are located.
        activity_to_id (dict): Dictionary mapping activity names to unique identifiers.
    """

    def __init__(self, xes_dir_path):
        """Initialize the XESParser with the directory path of XES files."""
        self.xes_dir_path = xes_dir_path
        self.activity_to_id = {}

    def parse_xes_event_log(self, xes_file_path, max_traces=100):
        """Parse a XES event log file.

        Args:
            xes_file_path (str): The file path of the XES file to be parsed.
            max_traces (int): The maximum number of traces to parse from the log.

        Returns:
            list: A list of parsed traces, where each trace is a list of event dictionaries.
        """
        traces = []
        try:
            print(f"Starting to parse the file: {xes_file_path}")
            tree = ET.parse(xes_file_path)
            root = tree.getroot()
            namespace = root.tag[root.tag.find("{"):root.tag.find("}")+1]
            processed_traces = 0

            for trace in root.findall(f"{namespace}trace"):
                if processed_traces >= max_traces:
                    print(f"Reached the limit of {max_traces} traces. Stopping.")
                    break
                events = []
                for event in trace.findall(f"{namespace}event"):
                    event_data = self.parse_event(event, namespace)
                    if event_data:
                        events.append(event_data)
                if events:
                    traces.append(events)
                    processed_traces += 1
                    if processed_traces % 10 == 0 or processed_traces == max_traces:
                        print(f"Processed {processed_traces}/{max_traces} traces.")

            print(f"Finished parsing {xes_file_path}. Total traces processed: {processed_traces}.")
        except ET.ParseError as e:
            print(f"Parse Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return traces

    def parse_event(self, event, namespace):
        """Parse an event from the XES log.

        Args:
            event (xml.etree.ElementTree.Element): The XML element representing the event.
            namespace (str): The XML namespace extracted from the log.

        Returns:
            dict: A dictionary of the parsed event data, or None if required attributes are missing.
        """
        event_data = {}
        concept_name = event.find(f"{namespace}string[@key='concept:name']")
        timestamp = event.find(f"{namespace}date[@key='time:timestamp']")

        if concept_name is not None and timestamp is not None:
            activity_name = concept_name.get('value')
            activity_timestamp = timestamp.get('value')
            timestamp_obj = date_parser.parse(activity_timestamp)

            event_data['concept:name'] = activity_name
            event_data['time:timestamp'] = timestamp_obj

            lifecycle_transition = event.find(f"{namespace}string[@key='lifecycle:transition']")
            if lifecycle_transition is not None:
                event_data['lifecycle:transition'] = lifecycle_transition.get('value')

            resource = event.find(f"{namespace}string[@key='org:resource']")
            if resource is not None:
                event_data['org:resource'] = resource.get('value')

            role = event.find(f"{namespace}string[@key='org:role']")
            if role is not None:
                event_data['org:role'] = role.get('value')

            group = event.find(f"{namespace}string[@key='org:group']")
            if group is not None:
                event_data['org:group'] = group.get('value')

            for attr in event:
                key = attr.get('key')
                if key not in event_data:
                    value = attr.get('value')
                    if attr.tag == f"{namespace}string":
                        event_data[key] = value
                    elif attr.tag == f"{namespace}date":
                        event_data[key] = date_parser.parse(value)

            return event_data
        else:
            print("Event missing name or timestamp")
            return None


    def process_all_xes_files(self, max_traces=100):
        """Process all XES files in the specified directory.

        Args:
            max_traces (int): The maximum number of traces to process across all files.

        Returns:
            list: A list of all traces processed from all files.
        """
        all_traces = []
        xes_files = [f for f in os.listdir(self.xes_dir_path) if f.endswith('.xes')]
        
        for file_name in xes_files:
            if len(all_traces) >= max_traces:
                break
            file_path = os.path.join(self.xes_dir_path, file_name)
            file_traces = self.parse_xes_event_log(file_path, max_traces=max_traces - len(all_traces))
            all_traces.extend(file_traces)
            print(f"File processed: {file_name}. Total traces collected: {len(all_traces)}")
            if len(all_traces) >= max_traces:
                print(f"Reached the overall limit of {max_traces} traces. Stopping.")
                break
        return all_traces


