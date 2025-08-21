with open("../test.log", "r", encoding="utf-8") as f:
    endpoints = {}
    endpointResponseTimes = {}
    responseTimes = []
    codes = {}
    unique_ids = []
    for line in f:
        if "POST" in line:
            log = line[line.find("POST"):]
            details = log.split()
            endpoint = details[1]
            code = details[2]
            responseTime = details[3]

            if endpoint not in endpoints:
                endpoints[endpoint] = 0
                endpointResponseTimes[endpoint] = []
            endpoints[endpoint] += 1
            if code not in codes:
                codes[code] = 0
            codes[code] += 1

            responseTimes.append(responseTime)
            endpointResponseTimes[endpoint].append(responseTime)
        
        if "[202" in line:
            id = line[line.find("[202")+1:-2]
            if id not in unique_ids:
                unique_ids.append(id)