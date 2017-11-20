import rospy
from AbstractAction import AbstractAction
from pnp_msgs.srv import PNPCondition, PNPConditionValue

class say(AbstractAction):

    def _start_action(self):
        rospy.loginfo('Saying "' + " ".join(self.params) + '"')
        #self.starting_time = rospy.Time.now()

    def _stop_action(self):
        rsopy.loginfo('Finished saying "' + " ".join(self.params) + '"')

    @classmethod
    def is_goal_reached(cls, params):
        ''' check conditions CurrentGoal and GoalStartingTime '''
        condition_value_sp = rospy.ServiceProxy("/PNPConditionValue", PNPConditionValue)
        condition_eval_sp = rospy.ServiceProxy("/PNPConditionEval", PNPCondition)

        # The goal is reached when we are actually saying what we want to say
        current_goal_cond = "CurrentGoal_" + cls.__name__ + "_" + "_".join(params)
        if condition_eval_sp(current_goal_cond).truth_value:
            starting_time = condition_value_sp("GoalStartingTime").value
            elapsed_time = rospy.Time.now() - rospy.Time.from_sec(float(starting_time))
            if elapsed_time.to_sec() > 4:
                return True

        return False
