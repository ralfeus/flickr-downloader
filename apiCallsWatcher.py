#!/usr/bin/env python3
from datetime import datetime
from retry.api import retry_call
import sys
import time

class apiCallsWatcher:
    startTime = datetime.now()
    callsCounter = 0
    expectedCallRate = 0.9

    @staticmethod
    def getRate():
        executionTime = (datetime.now() - apiCallsWatcher.startTime).seconds
        #print(executionTime)
        if executionTime == 0:
            executionTime = 0.00001
        callRate = apiCallsWatcher.callsCounter / executionTime
        #print(callRate)
        return callRate

    @staticmethod
    def manageCallRate():
        while apiCallsWatcher.getRate() > apiCallsWatcher.expectedCallRate:
            print("Waiting for call rate to lower from {0} to {1}".format(
                apiCallsWatcher.getRate(),
                apiCallsWatcher.expectedCallRate))
            time.sleep(1)

    @staticmethod
    def makeCall(call):
        def wrapper(*args, **kwargs):
            apiCallsWatcher.manageCallRate()
            print("Call: {0}, call rate: {1}".format(apiCallsWatcher.callsCounter + 1, apiCallsWatcher.getRate()), file = sys.stderr)
            value = retry_call(call, args, kwargs, tries = 3, delay = 2)
            apiCallsWatcher.callsCounter += 1
            return value
    
        return wrapper

@apiCallsWatcher.makeCall
def test(arg):
    time.sleep(random.randrange(3))
    print(arg)

def main():
    while True:
        test('Doing something')


