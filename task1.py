import argparse
from matplotlib import pyplot as plt

# Parse all the arguments using argparse to display the corresponding data
parser = argparse.ArgumentParser(description="Display report from the logs of CC's Timetable Generator")
parser.add_argument('-e', '--endpoints', action='store_true', help='Show endpoint popularity data')
parser.add_argument('-r', '--requests', action='store_true', help='Show API Requests and HTTP status codes count')
parser.add_argument('-t', '--times', action='store_true', help='Show response times statistics for each endpoint')
parser.add_argument('-T', '--timetable', action='store_true', help='Show timetable generation data')
parser.add_argument('-i', '--id', action='store_true', help='Show unique ID analysis')
args = parser.parse_args()

# If no arguments are given, then display all the data by default
if not (args.endpoints or args.requests or args.times or args.timetable or args.id):
    args.endpoints = args.requests = args.times = args.timetable = args.id = True

# Open the timetable.log file to read and parse the data
with open("timetable.log", "r", encoding="utf-8") as f:

    # Make dictionaries and lists to keep track of various data
    endpoints_count = {}
    endpoint_response_times = {}
    codes = {}
    unique_ids = []
    unique_ids_count = {}
    strategies_count = {"backtracking": 0, "sampling": 0}
    timetables_generated = []

    # Read the logs line by line, checking each line for any data we are interested in
    for line in f:

        # Check for POST request and parse the endpoint, status code, and time of the response
        if "POST" in line:
            log = line[line.find("POST"):]
            details = log.split()
            endpoint = details[1]
            code = details[2]
            response_time = details[3]

            if endpoint not in endpoints_count:
                endpoints_count[endpoint] = 0
                endpoint_response_times[endpoint] = []
            endpoints_count[endpoint] += 1

            if code not in codes:
                codes[code] = 0
            codes[code] += 1

            unit = response_time[-2:]
            response_time = float(response_time[:-2])
            if unit == "ms":
                response_time *= 1000

            endpoint_response_times[endpoint].append(response_time)
        
        # Check for unique IDs every time an ID appears in a line
        if "[202" in line:
            id = line[line.find("[202")+1:-2]
            batch = id[:4]
            if batch not in unique_ids_count:
                unique_ids_count[batch] = 0
            if id not in unique_ids:
                unique_ids.append(id)
                unique_ids_count[batch] += 1
        
        # Check for the strategy used for generating the timetables, and parse the number of timetables generated
        if "Backtracking" in line:
            strategies_count["backtracking"] += 1
        elif "Sampling" in line:
            strategies_count["sampling"] += 1
        if "Generation" in line:
            generated_num = line[line.find("Found"):].split()[1]
            timetables_generated.append(int(generated_num))


# Function for comparing and printing time with proper units
def formatted_time(time):
    if time >= 1000:
        time /= 1000
        unit = "ms"
    else:
        unit = "µs"
    return str(round(time, 2)) + " " + unit

# Display Results

# Traffic & Usage Analysis: Total API Requests, Endpoint Popularity, HTTP Status Codes
if args.endpoints or args.requests:
    print("-"*30 + "\nTraffic & Usage Analysis\n" + "-"*30)
    total_requests = sum([count for count in endpoints_count.values()])

if args.requests:
    # Total API Requests Logged
    print("Total API Requests Logged: " + str(total_requests))

    # HTTP Status Codes
    print("\nHTTP Status Codes:")
    for k, v in sorted(codes.items(), key=lambda x: x[1], reverse=True):
        print("  - " + k + ": " + str(v) + " times")

if args.endpoints:
    # Endpoint Popularity
    endpoints_percentages = {}
    print("\nEndpoint Popularity:")
    for k, v in sorted(endpoints_count.items(), key=lambda x: x[1], reverse=True):
        print("  - " + k + ": " + str(v) + " requests (" + str(round(v/total_requests*100, 1)) + "%)")
        endpoints_percentages[k] = v/total_requests*100

    # Pie Chart for Endpoint Popularity
    plt.pie(endpoints_percentages.values(),
            labels=endpoints_percentages.keys(),
            startangle=90,
            autopct='%1.1f%%')
    plt.title("Endpoint Popularity")
    plt.show()    

# Performance Metrics: Response times for each endpoint
if args.times:
    print("\n" + "-"*30 + "\nPerformance Metrics\n" + "-"*30)
    for endpoint in endpoint_response_times:
        print("Endpoint: " + endpoint)
        response_times = endpoint_response_times[endpoint]
        avg_time = sum(response_times) / len(response_times)
        print("  - Average Response Time: " + formatted_time(avg_time))
        print("  - Max Response Time: " + formatted_time(max(response_times)))

# Application-Specific Insights: Number of timetables generated, Strategy used
if args.timetable:
    print("\n" + "-"*30 + "\nApplication-Specific Insights\n" + "-"*30)
    print("Timetable Generation Strategy Usage:")
    print("  - Heuristic Backtracking: " + str(strategies_count["backtracking"]))
    print("  - Iterative Random Sampling: " + str(strategies_count["sampling"]))
    print("\nAverage Timetables Found per /generate call: " + str(round(sum(timetables_generated) / len(timetables_generated), 2)))
    print("Total number of timetables generated: " + str(sum(timetables_generated)))

# Unique ID Analysis: number of unique IDs in each batch
if args.id:
    print("\n" + "-"*30 + "\nUnique ID Analysis\n" + "-"*30)
    print("Total Unique IDs Found: " + str(sum(unique_ids_count.values())))
    unique_ids_count = dict(sorted(unique_ids_count.items(), key=lambda x: x[0]))
    for k, v in unique_ids_count.items():
        print("Batch of " + k + ": " + str(v) + " unique IDs")

    # Bar plot of number of unique IDs by batch
    plt.bar(unique_ids_count.keys(), unique_ids_count.values())
    plt.xlabel("Batch")
    plt.ylabel("Number of Users")
    plt.title("Number of Users by Batch")
    plt.show()