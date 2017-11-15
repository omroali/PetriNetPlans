from AbstractCondition import AbstractCondition
from std_msgs.msg import String

class closestNode(AbstractCondition):

    _topic_name = "/closest_node"

    _topic_type = String

    def evaluate(self, params):
        node = str(params[0])

        return node == self.last_data.data
