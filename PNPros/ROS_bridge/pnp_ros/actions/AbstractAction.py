import os
import sys
import rospy
import threading

from abc import ABC, abstractmethod
from pnp_msgs.msg import PNPActionFeedback, PNPResult

try:
    sys.path.append(os.environ["PNP_HOME"] + '/scripts')
except:
    print("Please set PNP_HOME environment variable to PetriNetPlans folder.")
    sys.exit(1)

import pnp_common
from pnp_common import *

class AbstractAction(ABC):

    def __init__(self, goalhandler, params):
        self.goalhandler = goalhandler
        self.params = params

        # create event for stopping the action
        self.cancel_event = threading.Event()

    @abstractmethod
    def _start_action(self):
        raise NotImplementedError()

    @abstractmethod
    def _stop_action(self):
        raise NotImplementedError()

    def _is_action_done(self):
        return self.is_goal_reached(self.params)

    @classmethod
    def is_goal_reached(cls, params):
        ''' Static definition of goal reached for the action '''
        raise NotImplementedError()

    ## main execution thread
    def _actionThread_exec(self):
        result = PNPResult()
        feedback = PNPActionFeedback()

        self._start_action()

        rospy.set_param(get_robot_key(PARAM_PNPACTIONSTATUS) + self.goalhandler.get_goal().name, ACTION_RUNNING)

        # rate 0.5hz
        r = rospy.Rate(2)

        # wait until the action is done
        while not self._is_action_done():
            # request to cancel action
            if self.cancel_event.isSet():
                break

            # send feedback
            feedback.feedback = 'running'
            self.goalhandler.publish_feedback(feedback)

            r.sleep()

        self._stop_action()

        rospy.set_param(get_robot_key(PARAM_PNPACTIONSTATUS) + self.goalhandler.get_goal().name, ACTION_SUCCESS)

        # send the result
        result.result = 'OK'
        self.goalhandler.set_succeeded(result, 'OK')


    def start_action(self):
        th = threading.Thread(None, self._actionThread_exec, args=())
        th.start()

    def interrupt_action(self):
        self.cancel_event.set()
