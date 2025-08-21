with open("timetable.log", "r", encoding="utf-8") as f:
    endpointsCount = {}
    endpointResponseTimes = {}
    codes = {}
    unique_ids = []
    for line in f:
        if "POST" in line:
            log = line[line.find("POST"):]
            details = log.split()
            endpoint = details[1]
            code = details[2]
            responseTime = details[3]

            if endpoint not in endpointsCount:
                endpointsCount[endpoint] = 0
                endpointResponseTimes[endpoint] = []
            endpointsCount[endpoint] += 1

            if code not in codes:
                codes[code] = 0
            codes[code] += 1

            unit = responseTime[-2:]
            responseTime = float(responseTime[:-2])
            if unit == "ms":
                responseTime *= 1000

            endpointResponseTimes[endpoint].append(responseTime)
        
        if "[202" in line:
            id = line[line.find("[202")+1:-2]
            if id not in unique_ids:
                unique_ids.append(id)

# Calculations

totalRequests = sum([count for count in endpointsCount.values()])

def formattedTime(time):
    if time >= 1000:
        time /= 1000
        unit = "ms"
    else:
        unit = "µs"
    return str(round(time, 2)) + " " + unit

# Display Results

print("Traffic & Usage Analysis\n\nTotal API Requests Logged: " + str(totalRequests))

print("\nEndpoint Popularity:")
for k, v in sorted(endpointsCount.items(), key=lambda x: x[1], reverse=True):
    print("  - " + k + ": " + str(v) + " requests (" + str(round(v/totalRequests*100, 1)) + "%)")

print("\nHTTP Status Codes:")
for k, v in sorted(codes.items(), key=lambda x: x[1], reverse=True):
    print("  - " + k + ": " + str(v) + " times")

print("\nPerformance Metrics\n")
for endpoint in endpointResponseTimes:
    print("Endpoint: " + endpoint)
    responseTimes = endpointResponseTimes[endpoint]
    avgTime = sum(responseTimes) / len(responseTimes)
    print("  - Average Response Time: " + formattedTime(avgTime))
    print("  - Max Response Time: " + formattedTime(max(responseTimes)))